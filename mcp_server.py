from mcp.server.mcpserver import MCPServer
from rag.search import search_cv as _search_cv
from tools.analyzer import analyze_job as _analyze_job

mcp = MCPServer("Job Match Advisor")

@mcp.tool(
    name="search_cv",
    description="Return the top_k CV chunks most relevant to the job text."
)
def search_cv(query: str, top_k: int = 3) -> list[str]:
    return _search_cv(query, top_k=top_k)

@mcp.tool(
    name="evaluate_job",
    description="Run the full analysis chain from job posting to final decision."
)
def evaluate_job(job_posting: str) -> dict:
    return _analyze_job(job_posting)

if __name__ == "__main__":
    mcp.run()