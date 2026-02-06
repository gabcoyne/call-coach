-- Migration: Create notifications and notification preferences tables
-- Description: Tables for in-app notifications and user notification preferences

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES speakers(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    read BOOLEAN DEFAULT false,
    archived BOOLEAN DEFAULT false,
    action_url VARCHAR(500),
    action_label VARCHAR(100),
    data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    read_at TIMESTAMP,
    created_at_idx TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at) (
    PARTITION p_notifications_older VALUES LESS THAN ('2025-01-01'),
    PARTITION p_notifications_2025_01 PARTITION BY RANGE (created_at) (
        PARTITION p_2025_01_01 VALUES LESS THAN ('2025-02-01'),
        PARTITION p_2025_01_02 VALUES LESS THAN ('2025-03-01'),
        PARTITION p_2025_01_03 VALUES LESS THAN ('2025-04-01'),
        PARTITION p_2025_01_04 VALUES LESS THAN ('2025-05-01'),
        PARTITION p_2025_01_05 VALUES LESS THAN ('2025-06-01'),
        PARTITION p_2025_01_06 VALUES LESS THAN ('2025-07-01'),
        PARTITION p_2025_01_07 VALUES LESS THAN ('2025-08-01'),
        PARTITION p_2025_01_08 VALUES LESS THAN ('2025-09-01'),
        PARTITION p_2025_01_09 VALUES LESS THAN ('2025-10-01'),
        PARTITION p_2025_01_10 VALUES LESS THAN ('2025-11-01'),
        PARTITION p_2025_01_11 VALUES LESS THAN ('2025-12-01'),
        PARTITION p_2025_01_12 VALUES LESS THAN ('2026-01-01')
    ),
    PARTITION p_notifications_future VALUES FROM UNBOUNDED
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, read) WHERE read = false;
CREATE INDEX IF NOT EXISTS idx_notifications_user_archived ON notifications(user_id, archived) WHERE archived = false;
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_notifications_expires_at ON notifications(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type);

-- Create user notification preferences table
CREATE TABLE IF NOT EXISTS user_notification_preferences (
    user_id UUID NOT NULL REFERENCES speakers(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,
    enabled BOOLEAN DEFAULT true,
    email BOOLEAN DEFAULT true,
    slack BOOLEAN DEFAULT true,
    in_app BOOLEAN DEFAULT true,
    frequency VARCHAR(50) DEFAULT 'immediate' CHECK (frequency IN ('immediate', 'daily_digest', 'weekly_digest', 'never')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, notification_type)
);

-- Indexes for preferences
CREATE INDEX IF NOT EXISTS idx_user_notification_prefs_enabled ON user_notification_preferences(enabled) WHERE enabled = true;
CREATE INDEX IF NOT EXISTS idx_user_notification_prefs_frequency ON user_notification_preferences(frequency);

-- Create notification delivery log table (for auditing)
CREATE TABLE IF NOT EXISTS notification_delivery_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_id UUID REFERENCES notifications(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    channel VARCHAR(50) NOT NULL CHECK (channel IN ('email', 'slack', 'in_app')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('sent', 'failed', 'bounced', 'unsubscribed')),
    error_message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for delivery log
CREATE INDEX IF NOT EXISTS idx_delivery_log_notification ON notification_delivery_log(notification_id);
CREATE INDEX IF NOT EXISTS idx_delivery_log_user ON notification_delivery_log(user_id);
CREATE INDEX IF NOT EXISTS idx_delivery_log_channel ON notification_delivery_log(channel);
CREATE INDEX IF NOT EXISTS idx_delivery_log_status ON notification_delivery_log(status);
CREATE INDEX IF NOT EXISTS idx_delivery_log_sent_at ON notification_delivery_log(sent_at);
