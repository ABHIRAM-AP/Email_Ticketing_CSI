-- ================================================
-- EVENT TICKETING SYSTEM - SUPABASE DATABASE SCHEMA
-- ================================================

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ================================================
-- EVENTS TABLE
-- ================================================
CREATE TABLE IF NOT EXISTS events (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('pre_event', 'hackathon_day')),
    event_date TIMESTAMPTZ NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    registration_open BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster queries
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_type ON events(event_type);

-- ================================================
-- REGISTRATIONS TABLE
-- ================================================
CREATE TABLE IF NOT EXISTS registrations (
    id BIGSERIAL PRIMARY KEY,
    event_id BIGINT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    college VARCHAR(200) NOT NULL,
    ticket_id VARCHAR(50) UNIQUE,
    qr_code_url TEXT,
    checked_in BOOLEAN DEFAULT FALSE,
    checked_in_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for faster queries
CREATE INDEX idx_registrations_event ON registrations(event_id);
CREATE INDEX idx_registrations_email ON registrations(email);
CREATE INDEX idx_registrations_ticket ON registrations(ticket_id);
CREATE UNIQUE INDEX idx_unique_event_email ON registrations(event_id, email);

-- ================================================
-- HACKATHON PARTICIPANTS TABLE (for CSV import)
-- ================================================
CREATE TABLE IF NOT EXISTS hackathon_participants (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    college VARCHAR(200),
    phone VARCHAR(20),
    imported_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster email lookups
CREATE INDEX idx_hackathon_email ON hackathon_participants(email);

-- ================================================
-- CHECK-INS TABLE (for tracking all check-ins)
-- ================================================
CREATE TABLE IF NOT EXISTS check_ins (
    id BIGSERIAL PRIMARY KEY,
    event_id BIGINT NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    ticket_id VARCHAR(50),
    source VARCHAR(20) NOT NULL CHECK (source IN ('qr', 'csv', 'manual')),
    checked_in_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_checkins_event ON check_ins(event_id);
CREATE INDEX idx_checkins_email ON check_ins(email);

-- ================================================
-- AUTOMATIC TIMESTAMP UPDATES
-- ================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_registrations_updated_at
    BEFORE UPDATE ON registrations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- ROW LEVEL SECURITY (Optional - for added security)
-- ================================================

-- Enable RLS on tables (uncomment if you want to use RLS)
-- ALTER TABLE events ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE registrations ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE hackathon_participants ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE check_ins ENABLE ROW LEVEL SECURITY;

-- Example policies (modify based on your needs)
-- Allow public read access to events
-- CREATE POLICY "Public can view events" ON events
--     FOR SELECT USING (true);

-- Only authenticated users can insert registrations
-- CREATE POLICY "Anyone can register" ON registrations
--     FOR INSERT WITH CHECK (true);

-- ================================================
-- SAMPLE DATA (Optional - for testing)
-- ================================================

-- Insert sample event
INSERT INTO events (name, description, event_type, event_date, capacity, registration_open)
VALUES 
    ('AI Workshop', 'Learn about AI and Machine Learning basics', 'pre_event', NOW() + INTERVAL '7 days', 100, TRUE),
    ('Coding Competition', 'Test your coding skills', 'hackathon_day', NOW() + INTERVAL '14 days', 150, TRUE);

-- ================================================
-- USEFUL QUERIES FOR REFERENCE
-- ================================================

-- Get event with registration count
-- SELECT e.*, COUNT(r.id) as registered_count
-- FROM events e
-- LEFT JOIN registrations r ON e.id = r.event_id
-- GROUP BY e.id;

-- Get all registrations for an event
-- SELECT * FROM registrations WHERE event_id = 1 ORDER BY created_at DESC;

-- Check if email is in hackathon participants
-- SELECT * FROM hackathon_participants WHERE email = 'user@example.com';

-- Get check-in stats for an event
-- SELECT 
--     source,
--     COUNT(*) as count
-- FROM check_ins
-- WHERE event_id = 1
-- GROUP BY source;