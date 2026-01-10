-- SQL script to restore admin permissions for chris@chasm.solutions
-- Run this directly in your PostgreSQL database if you have access

-- First, check if the user exists
SELECT id, email, name, role, can_admin, can_view_benchmark, can_edit_benchmark, can_moderate, can_manage_blog 
FROM users 
WHERE email = 'chris@chasm.solutions';

-- Update the user to have admin role and all permissions
UPDATE users 
SET 
    role = 'admin',
    can_admin = true,
    can_view_benchmark = true,
    can_edit_benchmark = true,
    can_moderate = true,
    can_manage_blog = true,
    updated_at = NOW()
WHERE email = 'chris@chasm.solutions';

-- Verify the update
SELECT id, email, name, role, can_admin, can_view_benchmark, can_edit_benchmark, can_moderate, can_manage_blog 
FROM users 
WHERE email = 'chris@chasm.solutions';
