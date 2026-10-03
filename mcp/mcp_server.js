import { McpServer } from "@modelcontextprotocol/server";
import { serveStdio } from "@modelcontextprotocol/server/stdio";
import * as z from "zod";

const jobs = [
    {
        title: "Software Engineer",
        location: "New York",
        description: "Develop and maintain software applications."
    },
    {
        title: "Data Scientist",
        location: "San Francisco",
        description: "Analyze and interpret complex data to help companies make decisions."
    },
    {
        title: "Product Manager",
        location: "Chicago",
        description: "Oversee the development and delivery of products."
    },
    {
        title: "UX Designer",
        location: "Los Angeles",
        description: "Design user interfaces and experiences for digital products."
    }
]



const server = new McpServer({
    name: "MCP Server",
    version: "1.0.0",
})
serveStdio(()=> {
    server.registerTool(
       "job_search",
        {
            title: "Job Search Tool",
            description: "A tool to search for jobs based on user input.",
            inputSchema: z.object({
                location: z.string().describe("The location to search for jobs."),
            })
        },

        async ({location}) => {
            const filteredJobs = jobs.filter(job => job.location.toLowerCase() === location.toLowerCase());

            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(filteredJobs)
                    }
                ]
            }

        }
    )

    return server;
})