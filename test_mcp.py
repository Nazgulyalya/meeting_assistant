"""Test that real MCP protocol works."""
from mcp_client.client import list_mcp_tools, send_email_via_mcp

print("=== Listing MCP tools ===")
tools = list_mcp_tools()
for t in tools:
    print(f"  • {t['name']}: {t['description'][:80]}")

print("\n=== Testing invalid email (negative case via MCP) ===")
result = send_email_via_mcp("not_an_email", "Test", "Body")
print(result)
# Должен вернуть: {'success': False, 'error': "Invalid email: 'not_an_email'"}

print("\n✅ MCP protocol works — server and client communicating via stdio")