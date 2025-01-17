-- =======================================================
-- Create User Procedure
-- =======================================================
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:      Dmitrievich Levin
-- Create Date: 08/2/2024
-- Description: Create User Row.
-- =============================================
CREATE PROCEDURE users.createUser
    (
    @user_id VARCHAR
)
AS
BEGIN
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON

    DECLARE @newUser TABLE (id CHAR)

    -- Create User WHERE NOT EXISTS
    INSERT INTO users
        (id)
    OUTPUT INSERTED.id INTO @newUser

    SELECT *
    FROM @newUser
END
GO
