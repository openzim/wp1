 ALTER TABLE pet ADD CONSTRAINT pet_id_constraint FOREIGN KEY (`pet_id`) REFERENCES pet_adoption (`id`);
 ALTER TABLE registration_code MODIFY status tinyint NOT NULL;
 ALTER TABLE user ADD COLUMN country_code varchar(10) NULL;