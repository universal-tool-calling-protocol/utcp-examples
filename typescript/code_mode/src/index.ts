/**
 * UTCP CodeMode Example - Complete Demonstration
 * 
 * This example shows how to use the CodeModeUtcpClient with file and direct-call plugins
 * to create powerful tool-calling workflows using TypeScript code execution.
 */

import { CodeModeUtcpClient } from '@utcp/code-mode';
import { addFunctionToUtcpDirectCall } from '@utcp/direct-call';
import '@utcp/file';  // Auto-registers the file plugin
import { FileCallTemplateSerializer } from '@utcp/file';
import * as path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// =============================================================================
// DIRECT-CALL TOOL IMPLEMENTATIONS
// =============================================================================

// Register the actual implementations of our tools as direct-call functions
console.log('🔧 Registering direct-call tool implementations...');

// Fibonacci calculator
addFunctionToUtcpDirectCall('fibonacci', async (n: number) => {
  console.log(`  📊 Computing Fibonacci(${n})`);
  
  if (n === 0) return { result: 0, sequence: [0] };
  if (n === 1) return { result: 1, sequence: [0, 1] };
  
  const sequence = [0, 1];
  let a = 0, b = 1;
  
  for (let i = 2; i <= n; i++) {
    const next = a + b;
    sequence.push(next);
    a = b;
    b = next;
  }
  
  return { result: b, sequence };
});

// Prime number checker
addFunctionToUtcpDirectCall('isPrime', async (number: number) => {
  console.log(`  🔍 Checking if ${number} is prime`);
  
  if (number < 2) return { isPrime: false, factors: [] };
  if (number === 2) return { isPrime: true, factors: [] };
  if (number % 2 === 0) return { isPrime: false, factors: [2, number / 2] };
  
  const factors: number[] = [];
  const sqrt = Math.sqrt(number);
  
  for (let i = 3; i <= sqrt; i += 2) {
    if (number % i === 0) {
      factors.push(i);
      if (i !== number / i) factors.push(number / i);
    }
  }
  
  if (factors.length > 0) {
    factors.sort((a, b) => a - b);
    factors.unshift(1);
    factors.push(number);
  }
  
  return { isPrime: factors.length === 0, factors };
});

// Text statistics analyzer
addFunctionToUtcpDirectCall('textStats', async (text: string, detailed: boolean = false) => {
  console.log(`  📝 Analyzing text (${text.length} characters)`);
  
  const words = text.toLowerCase().match(/\b\w+\b/g) || [];
  const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
  
  const wordFreq: { [key: string]: number } = {};
  words.forEach(word => {
    wordFreq[word] = (wordFreq[word] || 0) + 1;
  });
  
  const mostCommonWords = Object.entries(wordFreq)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5)
    .map(([word, count]) => ({ word, count }));
  
  const averageWordLength = words.length > 0 
    ? words.reduce((sum, word) => sum + word.length, 0) / words.length 
    : 0;
  
  return {
    wordCount: words.length,
    charCount: text.length,
    sentenceCount: sentences.length,
    averageWordLength: Math.round(averageWordLength * 100) / 100,
    mostCommonWords
  };
});

// Password generator
addFunctionToUtcpDirectCall('generatePassword', async (
  length: number = 12,
  includeNumbers: boolean = true,
  includeSymbols: boolean = true,
  excludeSimilar: boolean = true
) => {
  console.log(`  🔐 Generating ${length}-character password`);
  
  let chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
  if (includeNumbers) chars += '0123456789';
  if (includeSymbols) chars += '!@#$%^&*()_+-=[]{}|;:,.<>?';
  
  if (excludeSimilar) {
    chars = chars.replace(/[0O1lI]/g, '');
  }
  
  let password = '';
  for (let i = 0; i < length; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  
  // Simple strength assessment
  const hasLower = /[a-z]/.test(password);
  const hasUpper = /[A-Z]/.test(password);
  const hasNumber = /\d/.test(password);
  const hasSymbol = /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password);
  
  const complexity = [hasLower, hasUpper, hasNumber, hasSymbol].filter(Boolean).length;
  const entropy = Math.log2(chars.length) * length;
  
  let strength: string;
  if (length < 6 || complexity < 2) strength = 'weak';
  else if (length < 8 || complexity < 3) strength = 'medium';
  else if (length < 12 || complexity < 4) strength = 'strong';
  else strength = 'very-strong';
  
  return { password, strength, entropy: Math.round(entropy * 100) / 100 };
});

// Additional direct-call utility functions
addFunctionToUtcpDirectCall('wait', async (ms: number) => {
  console.log(`  ⏳ Waiting ${ms}ms`);
  await new Promise(resolve => setTimeout(resolve, ms));
  return { waited: ms, timestamp: Date.now() };
});

addFunctionToUtcpDirectCall('randomNumber', async (min: number = 1, max: number = 100) => {
  const result = Math.floor(Math.random() * (max - min + 1)) + min;
  console.log(`  🎲 Generated random number: ${result} (${min}-${max})`);
  return { number: result, min, max };
});

// =============================================================================
// MAIN DEMONSTRATION
// =============================================================================

async function runExample() {
  console.log('🚀 Starting UTCP CodeMode Example');
  console.log('==================================');

  try {
    // Create CodeModeUtcpClient
    console.log('\n1️⃣  Creating CodeModeUtcpClient...');
    const client = await CodeModeUtcpClient.create();

    // Register manual from JSON file using file plugin
    console.log('\n2️⃣  Loading manual from file...');
    const manualPath = path.resolve(__dirname, '../utcp_manual.json');
    
    await client.registerManual(new FileCallTemplateSerializer().validateDict({
      name: 'example_tools',
      call_template_type: 'file',
      file_path: manualPath
    }));

    // Register the utility manual provider
    addFunctionToUtcpDirectCall('getUtilityManual', async () => {
      return {
        utcp_version: '1.0.0',
        manual_version: '1.0.0',
        tools: [
          {
            name: 'wait',
            description: 'Waits for a specified number of milliseconds',
            inputs: {
              type: 'object',
              properties: {
                ms: { type: 'number', minimum: 0, description: 'Milliseconds to wait' }
              },
              required: ['ms']
            },
            outputs: {
              type: 'object',
              properties: {
                waited: { type: 'number', description: 'Milliseconds waited' },
                timestamp: { type: 'number', description: 'Timestamp when completed' }
              },
              required: ['waited', 'timestamp']
            },
            tags: ['utility', 'time'],
            tool_call_template: {
              call_template_type: 'direct-call',
              callable_name: 'wait'
            }
          },
          {
            name: 'randomNumber',
            description: 'Generates a random number within a range',
            inputs: {
              type: 'object',
              properties: {
                min: { type: 'number', default: 1, description: 'Minimum value' },
                max: { type: 'number', default: 100, description: 'Maximum value' }
              },
              required: ['min', 'max']
            },
            outputs: {
              type: 'object',
              properties: {
                number: { type: 'number', description: 'Generated random number' },
                min: { type: 'number', description: 'Minimum value used' },
                max: { type: 'number', description: 'Maximum value used' }
              },
              required: ['number', 'min', 'max']
            },
            tags: ['utility', 'random'],
            tool_call_template: {
              call_template_type: 'direct-call',
              callable_name: 'randomNumber'
            }
          }
        ]
      };
    });

    // Register some additional direct-call tools
    console.log('\n3️⃣  Registering additional direct-call tools...');
    await client.registerManual({
      name: 'utilities',
      call_template_type: 'direct-call',
      callable_name: 'getUtilityManual'
    });

    // Show registered tools
    console.log('\n4️⃣  Listing all registered tools...');
    const tools = await client.getTools();
    console.log(`Found ${tools.length} tools:`);
    tools.forEach((tool: any) => {
      console.log(`  • ${tool.name} - ${tool.description}`);
    });

    // Generate TypeScript interfaces
    console.log('\n5️⃣  Generating TypeScript interfaces...');
    const interfaces = await client.getAllToolsTypeScriptInterfaces();
    console.log('Generated interfaces:');
    console.log(interfaces);

    // Show the agent prompt template
    console.log('\n📋 Agent prompt template:');
    console.log('=====================================');
    console.log(CodeModeUtcpClient.AGENT_PROMPT_TEMPLATE);

    // =======================================================================
    // DEMONSTRATION 1: Simple Tool Usage
    // =======================================================================
    console.log('\n6️⃣  Demo 1: Simple tool usage...');
    const demo1Result = await client.callToolChain(`
      // Calculate some Fibonacci numbers
      const fib10 = await example_tools.fibonacci({ n: 10 });
      console.log('Fibonacci(10):', fib10.result);
      
      // Check if some numbers are prime
      const prime17 = await example_tools.isPrime({ number: 17 });
      const prime15 = await example_tools.isPrime({ number: 15 });
      
      return {
        fibonacci10: fib10.result,
        fibonacci10Sequence: fib10.sequence,
        is17Prime: prime17.isPrime,
        is15Prime: prime15.isPrime,
        factorsOf15: prime15.factors
      };
    `);
    
    console.log('Demo 1 Results:', JSON.stringify(demo1Result, null, 2));

    // =======================================================================
    // DEMONSTRATION 2: Text Analysis
    // =======================================================================
    console.log('\n7️⃣  Demo 2: Text analysis...');
    const demo2Result = await client.callToolChain(`
      // Analyze some text
      const sampleText = "The quick brown fox jumps over the lazy dog. This pangram contains every letter of the alphabet at least once. It's commonly used for testing fonts and keyboards.";
      
      const analysis = await example_tools.textStats({ text: sampleText, detailed: true });
      
      // Generate a password
      const password = await example_tools.generatePassword({ 
        length: 16, 
        includeNumbers: true, 
        includeSymbols: true 
      });
      
      return {
        textAnalysis: analysis,
        generatedPassword: {
          password: password.password,
          strength: password.strength,
          entropy: password.entropy
        }
      };
    `);
    
    console.log('Demo 2 Results:', JSON.stringify(demo2Result, null, 2));

    // =======================================================================
    // DEMONSTRATION 3: Complex Tool Chaining
    // =======================================================================
    console.log('\n8️⃣  Demo 3: Complex tool chaining...');
    const demo3Result = await client.callToolChain(`
      // Generate some random numbers and analyze them
      console.log('Generating random numbers...');
      const random1 = await utilities.randomNumber({ min: 10, max: 50 });
      const random2 = await utilities.randomNumber({ min: 10, max: 50 });
      const random3 = await utilities.randomNumber({ min: 10, max: 50 });
      
      console.log('Random numbers:', [random1.number, random2.number, random3.number]);
      
      // Check if any of them are prime
      const primeChecks = [];
      for (const num of [random1.number, random2.number, random3.number]) {
        const check = await example_tools.isPrime({ number: num });
        primeChecks.push({
          number: num,
          isPrime: check.isPrime,
          factors: check.factors
        });
      }
      
      // Calculate Fibonacci for the largest prime number (or largest number if no primes)
      const primeNumbers = primeChecks.filter(check => check.isPrime);
      const targetNumber = primeNumbers.length > 0 
        ? Math.max(...primeNumbers.map(p => p.number))
        : Math.max(random1.number, random2.number, random3.number);
      
      console.log('Calculating Fibonacci for:', targetNumber);
      
      // Wait a bit for dramatic effect
      await utilities.wait({ ms: 1000 });
      
      const fibResult = await example_tools.fibonacci({ n: Math.min(targetNumber, 25) }); // Cap at 25 to avoid huge numbers
      
      // Create a summary text and analyze it
      const summary = \`Analysis complete! We generated three random numbers: \${random1.number}, \${random2.number}, and \${random3.number}. Among these, \${primeNumbers.length} were prime numbers. We then calculated the Fibonacci sequence up to position \${Math.min(targetNumber, 25)}, which resulted in \${fibResult.result}.\`;
      
      const summaryStats = await example_tools.textStats({ text: summary });
      
      return {
        randomNumbers: [random1.number, random2.number, random3.number],
        primeAnalysis: primeChecks,
        targetNumber: targetNumber,
        fibonacciResult: fibResult.result,
        fibonacciSequenceLength: fibResult.sequence.length,
        summary: summary,
        summaryStats: {
          wordCount: summaryStats.wordCount,
          charCount: summaryStats.charCount,
          averageWordLength: summaryStats.averageWordLength
        },
        executionComplete: true
      };
    `, 30000); // 30 second timeout for this complex operation
    
    console.log('Demo 3 Results:', JSON.stringify(demo3Result, null, 2));

    // =======================================================================
    // DEMONSTRATION 4: Interface Access and Introspection
    // =======================================================================
    console.log('\n9️⃣  Demo 4: Interface access and introspection...');
    const demo4Result = await client.callToolChain(`
      // Access TypeScript interface definitions at runtime
      console.log('Interface access demonstration:');
      
      // Check what interfaces are available
      const hasInterfaces = typeof __interfaces === 'string' && __interfaces.length > 0;
      const containsNamespaces = __interfaces.includes('namespace example_tools') && __interfaces.includes('namespace utilities');
      
      // Get specific tool interface
      const fibonacciInterface = __getToolInterface('example_tools.fibonacci');
      const randomNumberInterface = __getToolInterface('utilities.randomNumber');
      
      // Extract some information from the interfaces
      const fibInterfacePreview = fibonacciInterface ? fibonacciInterface.substring(0, 200) + '...' : 'Not found';
      
      // Count available namespaces
      const namespaceMatches = __interfaces.match(/namespace \\w+/g) || [];
      const uniqueNamespaces = [...new Set(namespaceMatches)];
      
      return {
        runtimeIntrospection: {
          hasInterfaces,
          containsNamespaces,
          namespaceCount: uniqueNamespaces.length,
          availableNamespaces: uniqueNamespaces,
          totalInterfaceLength: __interfaces.length
        },
        specificTools: {
          fibonacciInterfaceFound: !!fibonacciInterface,
          randomNumberInterfaceFound: !!randomNumberInterface,
          fibonacciInterfacePreview: fibInterfacePreview
        },
        introspectionCapabilities: {
          canGetToolInterface: typeof __getToolInterface === 'function',
          canAccessAllInterfaces: typeof __interfaces === 'string',
          runtimeTypeInformation: true
        }
      };
    `);
    
    console.log('Demo 4 Results:', JSON.stringify(demo4Result, null, 2));

    // =======================================================================
    // DEMONSTRATION 5: Error Handling
    // =======================================================================
    console.log('\n🔟 Demo 5: Error handling...');
    try {
      await client.callToolChain(`
        // This should cause an error (negative Fibonacci)
        const result = await example_tools.fibonacci({ n: -5 });
        return result;
      `);
    } catch (error) {
      console.log('Caught expected error:', (error as Error).message);
    }

    // Demonstrate handling tool errors gracefully
    const demo5Result = await client.callToolChain(`
      const results = [];
      
      // Try some operations that might fail
      try {
        const validFib = await example_tools.fibonacci({ n: 5 });
        results.push({ operation: 'fibonacci(5)', success: true, result: validFib.result });
      } catch (error) {
        results.push({ operation: 'fibonacci(5)', success: false, error: error.message });
      }
      
      try {
        const prime = await example_tools.isPrime({ number: 97 });
        results.push({ operation: 'isPrime(97)', success: true, result: prime.isPrime });
      } catch (error) {
        results.push({ operation: 'isPrime(97)', success: false, error: error.message });
      }
      
      return {
        testResults: results,
        allTestsCompleted: true
      };
    `);
    
    console.log('Demo 5 Results:', JSON.stringify(demo5Result, null, 2));

    // Cleanup
    await client.close();
    
    console.log('\n✅ All demonstrations completed successfully!');
    console.log('\n🎉 CodeModeUtcpClient example finished!');
    console.log('\nKey features demonstrated:');
    console.log('• Loading tools from JSON file using file plugin');
    console.log('• Registering direct-call tool implementations');
    console.log('• Hierarchical TypeScript interface generation');
    console.log('• Hierarchical tool access (manual.tool) patterns');
    console.log('• Runtime interface introspection and access');
    console.log('• Simple tool calls within executed code');
    console.log('• Complex tool chaining and data flow');
    console.log('• Error handling and graceful degradation');
    console.log('• Async operations and timeouts');

  } catch (error) {
    console.error('❌ Error in example:', error);
    process.exit(1);
  }
}

// Run the example
runExample().catch(console.error);
