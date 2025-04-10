import { Injectable } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

@Injectable()
export class AppService {
  async getHello(): Promise<any> {  // Change return type to any to include image
    try {
      const { stdout, stderr } = await execPromise('python Scanner.py', {
        cwd: process.cwd(),
        timeout: 30000
      });

      console.log('Python stdout:', stdout);
      console.log('Python stderr:', stderr);

      if (stderr) {
        console.error(`Error from Python script: ${stderr}`);
      }

      if (!stdout || stdout.trim() === '') {
        return { status: 'error', message: 'No output from Python script' };
      }

      const result = JSON.parse(stdout.trim());
      return result;  // Return the full JSON object (including image)
    } catch (error) {
      console.error(`Failed to execute Python script: ${error}`);
      return { status: 'error', message: `Unable to capture fingerprint. Details: ${error.message}` };
    }
  }
}