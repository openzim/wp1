-- Up migration
-- z_status ENUM mein 'DELETED' ko add karna
ALTER TABLE zim_tasks MODIFY COLUMN z_status ENUM('PENDING', 'PROCESSING', 'FILE_READY', 'FAILED', 'DELETED');

-- Down migration (Backup ke liye)
-- rollback karne par purane status par wapas le jana
-- ALTER TABLE zim_tasks MODIFY COLUMN z_status ENUM('PENDING', 'PROCESSING', 'FILE_READY', 'FAILED');