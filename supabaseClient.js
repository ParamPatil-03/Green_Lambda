const supabaseUrl = 'https://lltanwbmvbfabzyxygpd.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxsdGFud2JtdmJmYWJ6eXh5Z3BkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4NzE1NTEsImV4cCI6MjA4OTQ0NzU1MX0.TRG9zfe5q5qh3aSD_LTXFBdTFONAFhW_e6C-R897vD8';

// Initialize the Supabase client
const supabase = window.supabase.createClient(supabaseUrl, supabaseAnonKey);

// You can test the connection by logging it
console.log('Supabase client initialized!', supabase);
