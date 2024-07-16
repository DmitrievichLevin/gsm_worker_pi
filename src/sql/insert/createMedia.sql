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
CREATE PROCEDURE media.createMeta
    (
    -- params
    @id VARCHAR,
    @user_id VARCHAR,
    @bucket VARCHAR,
    @doc VARCHAR,
    @doc_path VARCHAR,
    @file_ext VARCHAR,
    @file_size BIGINT,
    @thumb_size BIGINT
)
AS
BEGIN
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON

    DECLARE @newUser TABLE (ID CHAR)

    -- Create User WHERE NOT EXISTS
    INSERT INTO users
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
    INSERT INTO media
        (id, user_id, bucket, doc, doc_path, file_ext, file_size, thumb_size, created_at)
    OUTPUT 
        INSERTED.*, UNIX_TIMESTAMP(INSERTED.created_at) AS created_at 
        INTO #newMedia
    VALUES(@id, @user_id, @bucket, @doc, @doc_path, @file_ext, @file_size, @thumb_size, CURRENT_TIMESTAMP)

    SELECT *
    FROM #newMedia
END
GO
