-- =======================================================
-- Delete Media Procedure
-- =======================================================
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
-- =============================================
-- Author:      Dmitrievich Levin
-- Create Date: 08/2/2024
-- Description: Delete Media Metadata Row.
-- =============================================
IF NOT EXISTS (SELECT *
FROM sys.objects
WHERE type = 'P' AND OBJECT_ID = OBJECT_ID('deleteMedia'))
   exec('CREATE PROCEDURE [dbo].[deleteMedia] AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[deleteMedia]
    @id VARCHAR(255)
AS
BEGIN
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON

    DELETE FROM [dbo].[media]
    -- Output deleted row ID
    OUTPUT DELETED.id
    WHERE id = @id
END
GO
