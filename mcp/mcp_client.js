import "dotenv/config";
import { Client } from '@modelcontextprotocol/client';
import { StdioClientTransport } from "@modelcontextprotocol/client/stdio";
import OpenAI from "openai";

const mcpClient = new Client({
    name: "MCP Client",
    version: "1.0.0"
})


const transport = new StdioClientTransport({
    command: "node",
    args: ["mcp_server.js"],
});


const ai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
})



await mcpClient.connect(transport);
const { tools } = await mcpClient.listTools()

const openAiTools = tools.map((tool) => ({
    type: "function",

    name: tool.name,

    description: tool.description,

    parameters: tool.inputSchema
}))


async function main() {


    const userQuery = "Find software engineering jobs in Los Angeles";


    const response = await ai.responses.create({
        model: "gpt-5.4-mini",
        input: userQuery,
        tools: openAiTools
    })


    // console.log(response)


    for (let tool of response.output) {
        if (tool.type === "function_call") {
            const toolName = tool.name;
            const toolInput = JSON.parse(tool.arguments);

            const toolResponse = await mcpClient.callTool({
                name: toolName, arguments: toolInput
            });

        

            const finalResponse = await ai.responses.create({
                model: "gpt-5.4-mini",

                input: [
                    {
                        role: "user",
                        content: userQuery
                    },

                    ...response.output,

                    {
                        type: "function_call_output",
                        call_id: tool.call_id,
                        output: JSON.stringify(toolResponse)
                    }
                ],

                tools: openAiTools
            });

            console.log(finalResponse.output_text)
            break;
        }
    }
}

main()