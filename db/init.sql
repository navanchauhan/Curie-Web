create table curieweb (    id varchar(16) primary key, email nvarchar(255) NOT NULL,   protein LONGBLOB NOT NULL, protein_name VARCHAR(255),  ligand_pdbqt LONGBLOB,   ligand_smile VARCHAR(255),   ligand_name VARCHAR(255),   config LONGBLOB NOT NULL, date DATE, description VARCHAR(255),   done TINYINT DEFAULT 0, pdb VARCHAR(4),csv longblob)