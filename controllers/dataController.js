// Database.js
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://gnhhkqqahqwdfszpiyfb.supabase.co';
const supabaseKey = process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// ========================
// Interaction Data
// ========================

async function fetchInteractionsCountByMonth(targetMonth) {
  const { data, error } = await supabase.rpc('get_interactions_by_month', { target_month: targetMonth });

  if (error) {
    console.error('Error fetching interactions:', error);
    return null;
  }

  return data.length;
}

async function fetchLastFiveMonthsInteractions() {
  const results = {};
  const currentDate = new Date();

  for (let i = 0; i < 5; i++) {
    const targetMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() - i, 1);
    const formattedMonth = targetMonth.toISOString().split('T')[0];
    const count = await fetchInteractionsCountByMonth(formattedMonth);
    results[formattedMonth] = count;
  }

  console.log('Interaction counts for the current month and past 4 months:', results);
  return results;
}

// ========================
// Category Data
// ========================

async function fetchCategoryCount(category) {
  const { data, error } = await supabase.rpc('get_enquiry_by_category', {
    target_category: category
  });

  if (error) {
    console.error(`Error fetching category '${category}':`, error);
    return 0;
  }

  return data.length || 0;
}

async function fetchAllCategoryCounts() {
  const categories = [
    'Colour_of_water', 'Taste_of_water', 'Smell_of_water',
    'Water_pressure', 'Water_leakage', 'Water_quality',
    'Water_temperature', 'Flooding', 'Testing_services', 'Other'
  ];

  const results = {};
  for (const category of categories) {
    const count = await fetchCategoryCount(category);
    results[category] = count;
  }

  console.log('Category counts:', results);
  return results;
}

async function createEnquiry(description, category, sentiment) {
  const { data, error } = await supabase.rpc('create_enquiry', {
    new_description: description,
    new_category: category,
    new_sentiment: sentiment
  });

  if (error) {
    console.error('Error creating enquiry:', error);
    return null;
  }

  console.log('Enquiry created:', data);
  return data;
}

// ========================
// Exports
// ========================

module.exports = {
  fetchInteractionsCountByMonth,
  fetchLastFiveMonthsInteractions,
  fetchCategoryCount,
  fetchAllCategoryCounts,
  createEnquiry
};
