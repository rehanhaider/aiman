// GitHub client for post-review and review.js: App JWT, installation
// lookup, a token for one repo, reads of the PR, its files, diff and review
// threads, the PR head check, and a COMMENT review. Every failure is a
// GitHubClientError whose code matches the post-review error contract.
import { sign } from "node:crypto";
const API_URL = "https://api.github.com";
const API_VERSION = "2022-11-28";
const USER_AGENT = "mizcode-reviewer";
export class GitHubClientError extends Error {
    code;
    status;
    currentHead;
    constructor(code, message, extra = {}) {
        super(message);
        this.name = "GitHubClientError";
        this.code = code;
        this.status = extra.status;
        this.currentHead = extra.currentHead;
    }
}
function base64url(input) {
    return Buffer.from(input).toString("base64url");
}
// RS256 JWT for the App. iat is backdated 60s for clock drift and exp stays
// under GitHub's 10-minute limit.
export function createAppJwt(appId, privateKey, now = Date.now()) {
    const seconds = Math.floor(now / 1000);
    const header = base64url(JSON.stringify({ alg: "RS256", typ: "JWT" }));
    const payload = base64url(JSON.stringify({ iat: seconds - 60, exp: seconds + 540, iss: appId }));
    const signature = sign("sha256", Buffer.from(`${header}.${payload}`), privateKey);
    return `${header}.${payload}.${base64url(signature)}`;
}
async function request(options, method, path, bearer, body, accept = "application/vnd.github+json") {
    const doFetch = options.fetch ?? fetch;
    const headers = {
        Accept: accept,
        Authorization: `Bearer ${bearer}`,
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": API_VERSION,
    };
    if (body !== undefined)
        headers["Content-Type"] = "application/json";
    return doFetch(`${options.baseUrl ?? API_URL}${path}`, {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
    });
}
async function githubError(response) {
    const text = await response.text();
    let message = text || response.statusText;
    try {
        const parsed = JSON.parse(text);
        if (typeof parsed.message === "string") {
            message = parsed.message;
            if (Array.isArray(parsed.errors) && parsed.errors.length > 0) {
                message += `: ${JSON.stringify(parsed.errors)}`;
            }
        }
    }
    catch {
        // Not JSON. Keep the raw text.
    }
    return new GitHubClientError("github_error", `GitHub returned ${response.status}: ${message}`, { status: response.status });
}
async function json(response) {
    if (!response.ok)
        throw await githubError(response);
    return (await response.json());
}
function repoPath(repo) {
    return `/repos/${encodeURIComponent(repo.owner)}/${encodeURIComponent(repo.name)}`;
}
export async function getInstallationId(repo, appJwt, options = {}) {
    const response = await request(options, "GET", `${repoPath(repo)}/installation`, appJwt);
    if (response.status === 404) {
        throw new GitHubClientError("not_installed", `The App is not installed on ${repo.owner}/${repo.name}. Install it on that repository and try again.`);
    }
    const installation = await json(response);
    return installation.id;
}
// Installation tokens last one hour. The repositories list limits this one
// to the single repo being reviewed.
export async function createInstallationToken(installationId, repo, appJwt, options = {}) {
    const response = await request(options, "POST", `/app/installations/${installationId}/access_tokens`, appJwt, { repositories: [repo.name] });
    const token = await json(response);
    return token.token;
}
// Signs in as the App and returns an installation token for the one repo.
export async function createRepoToken(appId, privateKey, repo, options = {}) {
    const appJwt = createAppJwt(appId, privateKey);
    const installationId = await getInstallationId(repo, appJwt, options);
    return createInstallationToken(installationId, repo, appJwt, options);
}
export async function getPullRequestHead(repo, pullNumber, token, options = {}) {
    const response = await request(options, "GET", `${repoPath(repo)}/pulls/${pullNumber}`, token);
    const pull = await json(response);
    return pull.head.sha;
}
export async function getPullRequest(repo, pullNumber, token, options = {}) {
    const response = await request(options, "GET", `${repoPath(repo)}/pulls/${pullNumber}`, token);
    const pull = await json(response);
    return {
        number: pull.number,
        title: pull.title,
        body: pull.body ?? "",
        url: pull.html_url,
        base: pull.base.ref,
        headSha: pull.head.sha,
        changedFiles: pull.changed_files,
        additions: pull.additions,
        deletions: pull.deletions,
    };
}
// GitHub lists at most 3000 files, 100 a page. A short page is the last one.
export async function listPullRequestFiles(repo, pullNumber, token, options = {}) {
    const files = [];
    for (let page = 1;; page++) {
        const response = await request(options, "GET", `${repoPath(repo)}/pulls/${pullNumber}/files?per_page=100&page=${page}`, token);
        const rows = await json(response);
        for (const row of rows)
            files.push({ path: row.filename, additions: row.additions, deletions: row.deletions });
        if (rows.length < 100)
            return files;
    }
}
// The whole PR diff against its base, as one unified diff.
export async function getPullRequestDiff(repo, pullNumber, token, options = {}) {
    const response = await request(options, "GET", `${repoPath(repo)}/pulls/${pullNumber}`, token, undefined, "application/vnd.github.diff");
    if (!response.ok)
        throw await githubError(response);
    return response.text();
}
const THREADS_QUERY = `query($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          isResolved
          isOutdated
          path
          line
          comments(first: 1) {
            totalCount
            nodes { author { login } body }
          }
        }
      }
    }
  }
}`;
// Review threads and whether each is resolved. Only GraphQL has this. When a
// later page fails, the error carries the threads read so far.
export class ReviewThreadsError extends GitHubClientError {
    threads;
    constructor(error, threads) {
        super(error.code, error.message, { status: error.status });
        this.name = "ReviewThreadsError";
        this.threads = threads;
    }
}
export async function getReviewThreads(repo, pullNumber, token, options = {}) {
    const threads = [];
    let cursor = null;
    for (;;) {
        let page;
        try {
            const response = await request(options, "POST", "/graphql", token, {
                query: THREADS_QUERY,
                variables: { owner: repo.owner, name: repo.name, number: pullNumber, cursor },
            });
            page = await json(response);
        }
        catch (error) {
            if (error instanceof GitHubClientError)
                throw new ReviewThreadsError(error, threads);
            // fetch throws without an HTTP status when GitHub cannot be reached.
            const cause = error.cause;
            const message = `Could not reach GitHub: ${cause?.message ?? error.message}`;
            throw new ReviewThreadsError(new GitHubClientError("github_error", message), threads);
        }
        const connection = page.data?.repository?.pullRequest?.reviewThreads;
        if (page.errors?.length || !connection) {
            const message = page.errors?.map((e) => e.message).join("; ") || "no reviewThreads in the response";
            throw new ReviewThreadsError(new GitHubClientError("github_error", `GitHub GraphQL returned an error: ${message}`), threads);
        }
        for (const node of connection.nodes) {
            const first = node.comments.nodes[0];
            threads.push({
                path: node.path,
                line: node.line,
                isResolved: node.isResolved,
                isOutdated: node.isOutdated,
                author: first?.author?.login ?? null,
                body: first?.body ?? "",
                commentCount: node.comments.totalCount,
            });
        }
        if (!connection.pageInfo.hasNextPage)
            return threads;
        cursor = connection.pageInfo.endCursor;
    }
}
export async function assertHead(repo, pullNumber, expectedSha, token, options = {}) {
    const currentHead = await getPullRequestHead(repo, pullNumber, token, options);
    if (currentHead !== expectedSha) {
        throw new GitHubClientError("head_moved", `The pull request head is now ${currentHead}, not ${expectedSha}. Review the new head and post again.`, { currentHead });
    }
}
// The event is always COMMENT. This client never approves or requests changes.
export async function postReview(repo, pullNumber, commitId, review, token, options = {}) {
    const response = await request(options, "POST", `${repoPath(repo)}/pulls/${pullNumber}/reviews`, token, {
        commit_id: commitId,
        body: review.body,
        event: "COMMENT",
        comments: review.comments,
    });
    const posted = await json(response);
    return { review_id: posted.id, html_url: posted.html_url };
}
// The whole flow: sign in as the App, get a token for the repo, refuse a moved
// head, then post.
export async function postReviewAsApp(input, options = {}) {
    const token = await createRepoToken(input.appId, input.privateKey, input.repo, options);
    await assertHead(input.repo, input.pullNumber, input.sha, token, options);
    return postReview(input.repo, input.pullNumber, input.sha, input.review, token, options);
}
