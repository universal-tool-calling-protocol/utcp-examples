# UTCP CodeMode Complete Example

This is a comprehensive, standalone example demonstrating the **UTCP CodeModeUtcpClient** with all its powerful features. This example shows how to use TypeScript code execution with direct access to registered tools.

## 🚀 Features Demonstrated

- ✅ **File Plugin Integration** - Load tool definitions from JSON files
- ✅ **Direct-Call Plugin Integration** - Register TypeScript/JavaScript functions as tools
- ✅ **TypeScript Interface Generation** - Auto-generate type-safe interfaces for all tools
- ✅ **Code Execution** - Run TypeScript code with direct access to tools as functions
- ✅ **Complex Tool Chaining** - Chain multiple tool calls with data flow
- ✅ **Error Handling** - Graceful error handling and recovery
- ✅ **Async Operations** - Support for async tools and operations
- ✅ **Real-world Examples** - Fibonacci, prime checking, text analysis, password generation

## 📁 Project Structure

```
example/
├── src/
│   └── index.ts              # Main demonstration code
├── utcp_manual.json          # Tool definitions loaded via file plugin
├── package.json              # Dependencies and scripts
├── tsconfig.json            # TypeScript configuration
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🛠️ Setup Instructions

### Prerequisites

- Node.js 18+ or Bun
- npm, yarn, or bun package manager

### Installation

1. **Copy this entire example folder** to your desired location
2. **Install dependencies**:

```bash
# Using npm
npm install

# Using yarn
yarn install

# Using bun
bun install
```

3. **Run the example**:

```bash
# Using npm
npm run dev

# Using yarn  
yarn dev

# Using bun
bun run src/index.ts
```

## 📋 What This Example Does

### 1. Tool Registration
- Loads tool definitions from `utcp_manual.json` using the **file plugin**
- Registers actual implementations using **direct-call plugin**
- Creates additional utility tools programmatically

### 2. Available Tools
- **`fibonacci`** - Calculate Fibonacci numbers with sequence
- **`isPrime`** - Check if numbers are prime with factorization  
- **`textStats`** - Analyze text for word count, sentences, etc.
- **`generatePassword`** - Generate secure passwords with strength analysis
- **`wait`** - Async wait utility
- **`randomNumber`** - Generate random numbers in range

### 3. Demonstrations

**Demo 1: Simple Tool Usage**
```typescript
const fib10 = await fibonacci({ n: 10 });
const prime17 = await isPrime({ number: 17 });
```

**Demo 2: Text Analysis**  
```typescript
const analysis = await textStats({ text: sampleText, detailed: true });
const password = await generatePassword({ length: 16 });
```

**Demo 3: Complex Tool Chaining**
```typescript
// Generate random numbers
const nums = await Promise.all([
  randomNumber({ min: 10, max: 50 }),
  randomNumber({ min: 10, max: 50 }),
  randomNumber({ min: 10, max: 50 })
]);

// Check which are prime
const primeChecks = [];
for (const num of nums) {
  const check = await isPrime({ number: num.number });
  primeChecks.push(check);
}

// Calculate Fibonacci for the largest prime
const fibResult = await fibonacci({ n: targetNumber });
```

**Demo 4: Error Handling**
```typescript
try {
  const validFib = await fibonacci({ n: 5 });
  results.push({ success: true, result: validFib.result });
} catch (error) {
  results.push({ success: false, error: error.message });
}
```

## 🔧 Customization

### Adding Your Own Tools

1. **Add tool definition** to `utcp_manual.json`:
```json
{
  "name": "myTool",
  "description": "My custom tool",
  "inputs": {
    "type": "object",
    "properties": {
      "input": { "type": "string" }
    },
    "required": ["input"]
  },
  "outputs": {
    "type": "object", 
    "properties": {
      "result": { "type": "string" }
    },
    "required": ["result"]
  },
  "tool_call_template": {
    "call_template_type": "direct-call",
    "callable_name": "myTool"
  }
}
```

2. **Register the implementation**:
```typescript
addFunctionToUtcpDirectCall('myTool', async (input: string) => {
  // Your implementation here
  return { result: `Processed: ${input}` };
});
```

3. **Use in code execution**:
```typescript
const result = await client.callToolChain(`
  const output = await myTool({ input: "Hello World" });
  return output.result;
`);
```

### Creating Different Tool Categories

You can organize tools into different manuals:

```typescript
// Math tools manual
await client.registerManual({
  name: 'math_tools',
  call_template_type: 'file', 
  path: './math_tools.json'
});

// Utility tools manual  
await client.registerManual({
  name: 'utilities',
  call_template_type: 'direct-call',
  callable_name: 'getUtilityManual' 
});
```

## 🎯 Key Concepts

### TypeScript Interface Generation
```typescript
const interfaces = await client.getAllToolsTypeScriptInterfaces();
console.log(interfaces);
// Outputs complete TypeScript interfaces for all tools
```

### Secure Code Execution
- Code runs in an isolated VM context
- Only registered tools are accessible
- Timeout protection prevents infinite loops
- Error boundaries prevent crashes

### Tool Function Mapping
- Tools registered as `manual.toolName` become functions named `toolName`
- Input validation based on JSON Schema
- Type-safe interfaces generated automatically

## 🚨 Important Notes

### Dependencies
This example requires these UTCP packages:
- `@utcp/code-mode` - Core CodeMode functionality
- `@utcp/direct-call` - Direct function calling
- `@utcp/file` - File-based tool loading
- `@utcp/sdk` - Core UTCP functionality

### Security Considerations
- Code execution happens in a VM sandbox
- No access to file system or Node.js modules by default
- Only registered tools are available in execution context
- Use timeouts to prevent runaway code

### Performance Tips
- Tool interface generation is cached automatically
- VM context creation is optimized for repeated use
- Use appropriate timeouts for long-running operations
- Consider tool complexity when chaining operations

## 📚 Further Reading

- [UTCP Documentation](https://github.com/universal-tool-calling-protocol)
- [CodeMode Plugin Documentation](../packages/code-mode/README.md)
- [Direct-Call Plugin Documentation](../packages/direct-call/README.md)  
- [File Plugin Documentation](../packages/file/README.md)

## 🐛 Troubleshooting

### Common Issues

**"Cannot find module" errors:**
- Ensure all dependencies are installed: `npm install`
- Check that you're using compatible Node.js version (18+)

**Tool not found errors:**
- Verify tool is registered in both JSON and implementation
- Check that manual registration succeeded without errors
- Ensure tool names match exactly (case-sensitive)

**Code execution timeouts:**
- Increase timeout parameter: `callToolChain(code, 60000)`  
- Check for infinite loops or blocking operations
- Use `await wait()` to add delays if needed

**Type errors:**
- Ensure JSON schema matches implementation
- Add `required` arrays to make properties non-optional
- Use generated interfaces for better IDE support

## 📄 License

This example is provided under the MIT License - see the parent project for full license details.

---

🎉 **Happy coding with UTCP CodeMode!**
