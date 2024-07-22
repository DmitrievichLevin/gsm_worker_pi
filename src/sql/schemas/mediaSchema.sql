CREATE TABLE media
(
    -- S3 Key
    id VARCHAR(255) NOT NULL PRIMARY KEY,
    -- S3 Dir (User ID)
    user_id VARCHAR(255) NOT NULL,
    -- S3 Bucket
    bucket VARCHAR(255) NOT NULL,
    -- Mongo Document
    doc VARCHAR(255) NOT NULL,
    -- Mongo Document Id
    doc_id VARCHAR (255) NOT NULL,
    -- Mongo Document Path eg. userInfo.profileImage
    doc_path VARCHAR(255),
    mime VARCHAR(255),
    file_ext VARCHAR(255),
    -- In Bytes (For Query of file list with size constraint)
    -- Media
    file_size BIGINT NOT NULL,
    -- Thumbnail
    thumb_size BIGINT NOT NULL,
    --
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    -- Index Mongo Doc For Optimized Query on Document Media
    INDEX fk_media_doc (doc ASC)
);
