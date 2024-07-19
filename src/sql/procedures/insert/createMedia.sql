-- =======================================================
-- Media Meta-Data
-- =======================================================
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:      Dmitrievich Levin
-- Create Date: 07/16/2024
-- Description: Creates Media metadata and user(if not exists).
-- =============================================
IF NOT EXISTS (SELECT *
FROM sys.objects
WHERE type = 'P' AND OBJECT_ID = OBJECT_ID('createMeta'))
   exec('CREATE PROCEDURE [dbo].[createMeta] AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[createMeta]
    (
    -- params
    @id VARCHAR(255),
    @user_id VARCHAR
(255),
    @bucket VARCHAR
(255),
    @doc VARCHAR
(255),
    @doc_id VARCHAR
(255),
    @doc_path VARCHAR
(255),
    @file_ext VARCHAR
(255),
    @file_size BIGINT,
    @thumb_size BIGINT
)
AS
BEGIN
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON

    DECLARE @newUser TABLE (ID VARCHAR(255))

    -- Create User WHERE NOT EXISTS
    INSERT INTO dbo.users
        (id)
    OUTPUT INSERTED.id INTO @newUser
    SELECT p.a
    FROM (VALUES
            (@user_id)) p(a)
    WHERE NOT EXISTS
	(SELECT 1
    FROM users
    WHERE id=@user_id)

    -- Guarentees Existing User
    INSERT INTO dbo.media
        (id, user_id, bucket, doc, doc_id, doc_path, file_ext, file_size, thumb_size, created_at)
    OUTPUT
    INSERTED.id,
    INSERTED.user_id
    AS
    'owner',
    INSERTED.doc,
    INSERTED.doc_id,
    INSERTED.doc_path,
    INSERTED.file_ext,
    INSERTED.file_size,
    INSERTED.thumb_size,
    DATEDIFF
    (SECOND,'1970-01-01',
    INSERTED.created_at)
    AS
    created_at
    VALUES
        (@id, @user_id, @bucket, @doc, @doc_id, @doc_path, @file_ext, @file_size, @thumb_size, CURRENT_TIMESTAMP)

END
GO
