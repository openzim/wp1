 ALTER TABLE vaccination ADD COLUMN pet_id bigint DEFAULT NULL;
 ALTER TABLE vaccination ADD CONSTRAINT vaccination_id_constraint FOREIGN KEY (`pet_id`) REFERENCES pet (`id`);