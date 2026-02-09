-- 1. Create the Database if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'master')
BEGIN
    CREATE DATABASE [master];
END;
GO

-- 2. Switch context to the new database
USE [master];
GO

-- 3. Create the 'users' table using MSSQL syntax
IF OBJECT_ID(N'dbo.users', N'U') IS NULL
BEGIN
    CREATE TABLE [dbo].[users] (
        [id] BIGINT IDENTITY(1,1) NOT NULL, -- Replaces MySQL AUTO_INCREMENT
        [handle] NVARCHAR(200) NOT NULL,      -- NVARCHAR for Unicode support
        CONSTRAINT [PK_users] PRIMARY KEY CLUSTERED ([id] ASC)
    );
END;
GO

-- 4. Seed initial data without creating duplicates
INSERT INTO [dbo].[users] ([handle])
SELECT v.[handle]
FROM (VALUES ('jdoe_99'), ('tech_wiz')) AS v([handle])
WHERE NOT EXISTS (
    SELECT 1 
    FROM [dbo].[users] u 
    WHERE u.[handle] = v.[handle]
);
GO