require('dotenv').config();
const { createClient } = require('@supabase/supabase-js');

const supabaseUrl = 'https://gnhhkqqahqwdfszpiyfb.supabase.co';
const supabaseKey = process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);
async function fetchUsers() {
  const { data, error } = await supabase
    .from('Users')
    .select();

  if (error) {
    console.error("Error fetching data:", error);
  } else {
    console.log("Data:", data);
  }
}

fetchUsers();
