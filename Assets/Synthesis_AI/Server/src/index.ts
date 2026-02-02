#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';

const UNITY_API_URL = process.env.UNITY_API_URL || 'http://localhost:8765';

interface UnityCommand {
  type: string;
  parameters?: Record<string, any>;
}

interface UnityResponse {
  success: boolean;
  message: string;
  data?: any;
  error?: string;
}

class SynthesisMCPServer {
  private server: Server;
  private axiosInstance;

  constructor() {
    this.server = new Server(
      {
        name: 'synthesis',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.axiosInstance = axios.create({
      baseURL: UNITY_API_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupToolHandlers();

    // Error handling
    this.server.onerror = (error) => console.error('[MCP Error]', error);
    process.on('SIGINT', async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  private setupToolHandlers() {
    // List all available Unity tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'unity_ping',
          description: 'Test connection to Unity Editor',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'unity_get_scene_info',
          description: 'Get information about the active Unity scene including name, path, and root GameObjects',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
        {
          name: 'unity_find_gameobject',
          description: 'Find a GameObject by name and get its properties',
          inputSchema: {
            type: 'object',
            properties: {
              name: {
                type: 'string',
                description: 'Name of the GameObject to find',
              },
            },
            required: ['name'],
          },
        },
        {
          name: 'unity_get_component',
          description: 'Get component data from a GameObject',
          inputSchema: {
            type: 'object',
            properties: {
              object: {
                type: 'string',
                description: 'GameObject name',
              },
              component: {
                type: 'string',
                description: 'Component type name (e.g., "RectTransform", "Image")',
              },
            },
            required: ['object', 'component'],
          },
        },
        {
          name: 'unity_get_component_value',
          description: 'Get a specific field value from a component',
          inputSchema: {
            type: 'object',
            properties: {
              object: {
                type: 'string',
                description: 'GameObject name',
              },
              component: {
                type: 'string',
                description: 'Component type name',
              },
              field: {
                type: 'string',
                description: 'Field or property name to read',
              },
            },
            required: ['object', 'component', 'field'],
          },
        },
        {
          name: 'unity_set_component_value',
          description: 'Set a specific field value on a component. Can modify positions, colors, sizes, etc.',
          inputSchema: {
            type: 'object',
            properties: {
              object: {
                type: 'string',
                description: 'GameObject name',
              },
              component: {
                type: 'string',
                description: 'Component type name',
              },
              field: {
                type: 'string',
                description: 'Field or property name to modify',
              },
              value: {
                description: 'New value (can be number, string, object for Vector3/Color, etc.)',
              },
              record: {
                type: 'boolean',
                description: 'Whether to record this change for persistence (optional, default false)',
              },
            },
            required: ['object', 'component', 'field', 'value'],
          },
        },
        {
          name: 'unity_get_hierarchy',
          description: 'Get the full hierarchy tree of a GameObject and its children',
          inputSchema: {
            type: 'object',
            properties: {
              object: {
                type: 'string',
                description: 'Root GameObject name (optional, gets all if not specified)',
              },
            },
          },
        },
        {
          name: 'unity_get_children',
          description: 'Get direct children of a GameObject',
          inputSchema: {
            type: 'object',
            properties: {
              object: {
                type: 'string',
                description: 'Parent GameObject name',
              },
            },
            required: ['object'],
          },
        },
        {
          name: 'unity_log',
          description: 'Log a message to Unity Console',
          inputSchema: {
            type: 'object',
            properties: {
              message: {
                type: 'string',
                description: 'Message to log',
              },
            },
            required: ['message'],
          },
        },
        {
          name: 'unity_send_chat',
          description: 'Send a message to the Unity chat window (for AI responses to user)',
          inputSchema: {
            type: 'object',
            properties: {
              message: {
                type: 'string',
                description: 'Message to send to the chat window',
              },
            },
            required: ['message'],
          },
        },
        {
          name: 'unity_check_messages',
          description: 'Check for new messages from user in Unity chat (poll this to see if user sent a message)',
          inputSchema: {
            type: 'object',
            properties: {},
          },
        },
      ],
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const toolName = request.params.name;
      const args = request.params.arguments || {};

      try {
        // Map MCP tool names to Unity command types
        const commandType = toolName.replace('unity_', '');
        const unityCommandType = this.mapToolToCommand(commandType);

        // Call Unity HTTP API
        const response = await this.callUnity(unityCommandType, args);

        return {
          content: [
            {
              type: 'text',
              text: response.success
                ? `✅ ${response.message}\n\n${response.data ? JSON.stringify(response.data, null, 2) : ''}`
                : `❌ ${response.message}${response.error ? '\n\nError: ' + response.error : ''}`,
            },
          ],
          isError: !response.success,
        };
      } catch (error) {
        if (axios.isAxiosError(error)) {
          // Unity not reachable
          if (error.code === 'ECONNREFUSED') {
            return {
              content: [
                {
                  type: 'text',
                  text: `❌ Cannot connect to Unity. Make sure:\n1. Unity Editor is running\n2. SynLinkEditor is active (check Console for startup message)\n3. HTTP server is listening on ${UNITY_API_URL}`,
                },
              ],
              isError: true,
            };
          }
          throw new McpError(
            ErrorCode.InternalError,
            `Unity API error: ${error.message}`
          );
        }
        throw error;
      }
    });
  }

  private mapToolToCommand(toolName: string): string {
    // Convert snake_case to PascalCase
    // e.g., "get_scene_info" → "GetSceneInfo"
    return toolName
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join('');
  }

  private async callUnity(
    commandType: string,
    parameters: Record<string, any>
  ): Promise<UnityResponse> {
    const command: UnityCommand = {
      type: commandType,
      parameters,
    };

    const response = await this.axiosInstance.post<UnityResponse>(
      '/execute',
      command
    );
    return response.data;
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Synthesis MCP server running on stdio');
    console.error(`Unity API: ${UNITY_API_URL}`);
  }
}

const server = new SynthesisMCPServer();
server.run().catch(console.error);
