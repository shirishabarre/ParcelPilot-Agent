"""
MCP Server: docs_server
Tool 1 of 3 (Document search/retrieval) — searches policies, SOPs, product
docs, and signed customer agreements. Enforces source authority (never
returns the deprecated policy; scopes contract visibility to the caller's
account) at this tool layer, not just via prompting.

Run standalone for debugging:  python mcp_servers/docs_server/server.py
"""
from mcp.server.fastmcp import FastMCP

from retriever import DocRetriever

mcp = FastMCP("parcelpilot-docs")
_retriever = DocRetriever()


@mcp.tool()
def search_documents(query: str, account_scope: str = "", top_k: int = 5) -> list[dict]:
    """
    Search ParcelPilot's policies, SOPs, product docs, and (if account_scope
    is given) that account's signed agreement. Deprecated documents are
    excluded automatically. Results are ranked by keyword relevance AND
    source authority (contract > current policy/SOP > product doc >
    historical ticket).

    Args:
        query: natural-language search text.
        account_scope: account_id (e.g. 'ACCT-001') to include that
            customer's contract in results and exclude other customers'
            contracts. Leave blank for general-policy-only search.
        top_k: max results to return.
    """
    scope = account_scope or None
    return _retriever.search(query, top_k=top_k, account_scope=scope)


@mcp.tool()
def get_document(doc_id: str) -> list[dict]:
    """
    Retrieve all chunks of a specific document by filename, e.g.
    '03_Cancellation_and_Service_Credit_SOP_v4.pdf'. Useful once
    search_documents has identified the right source and full context is
    needed.
    """
    return _retriever.get_document_chunks(doc_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")
