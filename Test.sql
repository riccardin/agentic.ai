CREATE OR ALTER PROCEDURE dbo.[uspGetQueueItemsFromBatch]
    @TopNum INT = 10,
    @Status NVARCHAR(50) = N'sent',
    @NumChannels INT = 2,
   -- @pStepNo INT = 3,
    @defaultOutputLocaleStep NVARCHAR(50) = N'en-US'
AS
BEGIN
    SET NOCOUNT ON;

    ;WITH TopBatches AS (
        SELECT TOP (@TopN)
               mbi.BatchId,
               mbi.CognitiveServiceJobID
        FROM dbo.MediaBatchInfo AS mbi WITH (READPAST)
        WHERE mbi.Status = @Status
          AND mbi.NumChannels = @NumChannels
        ORDER BY mbi.BatchId ASC
    )
    SELECT
           tb.BatchId,
           tb.CognitiveServiceJobID,
           mb.SecondaryMessageQueueId,
           mb.[Position] AS [Position],
           smq.[ParentID],
           smq.[OutputPath],
           smq.[Locale],
           ISNULL(smq.[OutputLocale], @defaultOutputLocaleStep) AS [OutputLocale],
           smq.[IsCancelled],
           smq.[ProcessCount],
           smq.[StatusLastCheckedDateTime],
           smq.[NumberChannels],
           smq.[ChannelID]
    FROM TopBatches AS tb
    OUTER APPLY (
        SELECT TOP 1
               m.SecondaryMessageQueueId,
               m.[Position]
        FROM dbo.MediaBatch AS m WITH (READPAST)
        WHERE m.BatchId = tb.BatchId
          AND m.SecondaryMessageQueueId IS NOT NULL
        ORDER BY m.[Position] ASC, m.ID ASC
    ) AS mb
    LEFT JOIN dbo.SecondaryMessageQueue AS smq WITH (ROWLOCK, UPDLOCK, READPAST)
      ON smq.SecondaryMessageQueueID = mb.SecondaryMessageQueueId
    -- AND smq.ProcessStep = @pStepNo
     AND smq.IsCancelled = 0
     AND smq.IsFailed = 0
     AND smq.StepInProgress = 0
     AND smq.ProcessCount = 0
    WHERE mb.SecondaryMessageQueueId IS NOT NULL
    ORDER BY tb.BatchId ASC, smq.SecondaryMessageQueueID ASC;
END
