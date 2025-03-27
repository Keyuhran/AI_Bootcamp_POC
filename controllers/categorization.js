// controllers/summarizeEmailBody.js
const { OpenAI } = require('openai');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.resolve(__dirname, '../.env') });

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});


async function categorizeEmail(new_description) {
  const prompt = `. DO NOT deviate from the names of the categories and only reply stricly with the given category names('Colour_of_water', 'Taste_of_water', 'Smell_of_water',
      'Water_pressure', 'Water_leakage', 'Water_quality',
      'Water_temperature', 'Flooding', 'Testing_services). Categorize the following text into one of these 9 categories.
      only if they do not fit any of the descriptions, you may mark them as 'Other'. only do this as a LAST RESORT: \n\n"${new_description}"`;

  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-3.5-turbo', 
      messages: [
        {
          role: 'user',
          content: prompt,
        },
      ],
      temperature: 0.1,
      max_tokens: 250,
    });

    return response.choices[0].message.content.trim();
  } catch (error) {
    console.error("🔴 Error during OpenAI Categorization:", error.message);
    return "Could not categorize.";
  }
}

module.exports = { categorizeEmail };