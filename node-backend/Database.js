// Database.js
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://gnhhkqqahqwdfszpiyfb.supabase.co';
const supabaseKey = process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

function getMonthDateRange(monthOffset) {
  const date = new Date();
  date.setMonth(date.getMonth() - monthOffset);
  const year = date.getFullYear();
  const month = date.getMonth();
  return {
    firstDay: new Date(year, month, 1),
    lastDay: new Date(year, month + 1, 0, 23, 59, 59, 999)
  };
}

async function fetchDataForMonth(monthOffset) {
  const { firstDay, lastDay } = getMonthDateRange(monthOffset);
  const { data, error } = await supabase
    .from('Interactions')
    .select('*', { count: 'exact' })
    .gte('date_created', firstDay.toISOString())
    .lte('date_created', lastDay.toISOString());

  if (error) {
    console.error(`Error fetching data for month offset ${monthOffset}:`, error);
    return [];
  }

  return data;
}

module.exports = {
  fetchCurrentMonthData: () => fetchDataForMonth(0),
  fetchLastMonthData: () => fetchDataForMonth(1),
  fetchTwoMonthsAgoData: () => fetchDataForMonth(2),
  fetchThreeMonthsAgoData: () => fetchDataForMonth(3),
  fetchFourMonthsAgoData: () => fetchDataForMonth(4),
};
