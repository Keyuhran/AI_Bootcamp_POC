// Database.js
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://gnhhkqqahqwdfszpiyfb.supabase.co';
const supabaseKey = process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// async function fetchAllInteractions() {
//     const { data, error } = await supabase
//         .from('Interactions')
//         .select('*');
//         return data

// }

// fetchAllInteractions().then(data => {
//     console.log(data);
//   }).catch(error => {
//     console.error('Error:', error);
//   });
  
// module.exports = {
//   fetchAllInteractions
// };


// async function to fetch interaction counts by month using SQL RPC function
async function fetchInteractionsCountByMonth(targetMonth) {
    const { data, error } = await supabase
      .rpc('get_interactions_by_month', { target_month: targetMonth });
  
    if (error) {
      console.error('Error fetching interactions:', error);
      return null;
    }
  
    return data.length;
  }
  
  // Function to automatically fetch counts for the current month and the past 4 months
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
  
  // Testing the function
  fetchLastFiveMonthsInteractions().then(counts => {
    console.log('Fetched counts:', counts);
  }).catch(error => {
    console.error('Error:', error);
  });
  
  module.exports = {
    fetchInteractionsCountByMonth,
    fetchLastFiveMonthsInteractions
  };
  