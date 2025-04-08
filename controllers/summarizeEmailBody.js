// controllers/summarizeEmailBody.js
const { OpenAI } = require('openai');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(__dirname, '../.env') });

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

async function summarizeEmail(emailBody) {
  const prompt = `Summarize the following email in 1-2 concise sentences:\n\n"${emailBody}"`;

  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo', 
      messages: [
        {
          role: 'user',
          content: prompt,
        },
      ],
      temperature: 0.3,
      max_tokens: 150,
    });

    return response.choices[0].message.content.trim();
  } catch (error) {
    console.error("🔴 Error during OpenAI summarization:", error.message);
    return "Could not generate summary.";
  }
}

module.exports = { summarizeEmail };
