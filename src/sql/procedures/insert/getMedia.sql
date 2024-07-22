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
-- Description: Get media rows.
-- =============================================
IF NOT EXISTS (SELECT *
FROM sys.objects
WHERE type = 'P' AND OBJECT_ID = OBJECT_ID('getMeta'))
   exec('CREATE PROCEDURE [dbo].[getMeta] AS BEGIN SET NOCOUNT ON; END')
GO
ALTER PROCEDURE [dbo].[getMeta]
    (
    -- params
    @doc VARCHAR
(255),
    @doc_id VARCHAR
(255)
)
AS
BEGIN
    -- SET NOCOUNT ON added to prevent extra result sets from
    -- interfering with SELECT statements.
    SET NOCOUNT ON
    DECLARE @hyph VARCHAR(100)='-'
    DECLARE @period VARCHAR(100)='.'
    DECLARE @thumb VARCHAR(100)='thumb'
    -- Get Media Meta Rows
    SELECT
        id,
        CONCAT(id, @hyph, mime ,@period, file_ext) AS image_key,
        CONCAT(id, @hyph, @thumb, @period, file_ext) AS thumb_key,
        doc,
        doc_id,
        user_id AS 'owner',
        mime,
        doc_path,
        file_ext,
        file_size,
        DATEDIFF
    (SECOND,'1970-01-01',
    created_at)
    FROM media
    WHERE doc = @doc AND doc_id = @doc_id

END
GO
