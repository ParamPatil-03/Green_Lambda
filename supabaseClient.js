// Supabase configuration
// Keys are loaded from window.__env
// which can be injected by the server or build process
const supabaseUrl = window.__env?.SUPABASE_URL || 'https://lltanwbmvbfabzyxygpd.supabase.co';
const supabaseAnonKey = window.__env?.SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxsdGFud2JtdmJmYWJ6eXh5Z3BkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM4NzE1NTEsImV4cCI6MjA4OTQ0NzU1MX0.TRG9zfe5q5qh3aSD_LTXFBdTFONAFhW_e6C-R897vD8';

if (!supabaseUrl || !supabaseAnonKey || supabaseAnonKey === '[REPLACE_WITH_YOUR_KEY]') {
    console.warn('[Green Lambda] Supabase keys not configured. Some features may not work.');
}

// Initialize the Supabase client attached natively to the global window
if (typeof window.supabase !== 'undefined' && window.supabase && typeof window.supabase.createClient === 'function') {
    window.supabaseClient = window.supabase.createClient(supabaseUrl, supabaseAnonKey);
    console.log('Supabase client initialized!', window.supabaseClient);
} else {
    window.supabaseClient = null;
}
