-- Add last_read_at columns to chat_rooms table
-- Migration: 001_add_last_read_at_to_chat_rooms
-- Date: 2025-12-29

ALTER TABLE chat_rooms
ADD COLUMN user1_last_read_at DATETIME NULL,
ADD COLUMN user2_last_read_at DATETIME NULL;
