CREATE TABLE [dbo].[stanovi_source](
	[id] [int] NOT NULL,
	[name] [varchar](45) NULL DEFAULT (NULL),
	PRIMARY KEY CLUSTERED ([id] ASC)
)
INSERT INTO stanovi_source VALUES(1, 'mojkvadrat');
INSERT INTO stanovi_source VALUES(2, 'halooglasi');

CREATE TABLE [dbo].[stanovi_heating_type](
	[id] [int] NOT NULL,
	[heat_type] [varchar](64) NULL,
	CONSTRAINT [pk_stanovi_heating_type] PRIMARY KEY CLUSTERED ([id] ASC)
)
INSERT INTO [stanovi_heating_type] VALUES(1, 'CG');
INSERT INTO [stanovi_heating_type] VALUES(2, 'EG');
INSERT INTO [stanovi_heating_type] VALUES(3, 'TA');
INSERT INTO [stanovi_heating_type] VALUES(4, 'Mermerni radijatori');
INSERT INTO [stanovi_heating_type] VALUES(5, 'Gas');
INSERT INTO [stanovi_heating_type] VALUES(6, 'Podno');
INSERT INTO [stanovi_heating_type] VALUES(7, 'Norveški radijatori');
INSERT INTO [stanovi_heating_type] VALUES(8, 'Kaljeva pec');
INSERT INTO [stanovi_heating_type] VALUES(9, 'Daljinsko grejanje');

CREATE TABLE [dbo].[stanovi_stanovi](
	[id] [int] NOT NULL,
	[id_source] [int] NOT NULL,
	[title] [varchar](1024) NOT NULL,
	[url] [varchar](1024) NOT NULL,
	[published_date] [date] NOT NULL,
	[modified_date] [date] NOT NULL,
	[inserted_date] [datetime] NOT NULL DEFAULT (getdate()),
	[type] [varchar](63) NOT NULL,
	[price] [float] NULL DEFAULT (NULL),
	[area] [float] NULL DEFAULT (NULL),
	[city] [varchar](63) NOT NULL,
	[municipality] [varchar](63) NOT NULL,
	[part] [varchar](63) NULL DEFAULT (NULL),
	[street] [varchar](64) NULL DEFAULT (NULL),
	[floor] [float] NULL DEFAULT (NULL),
	[total_floors] [int] NULL DEFAULT (NULL),
	[rooms] [float] NULL DEFAULT (NULL),
	[construction_year] [int] NULL DEFAULT (NULL),
	[heating_type_id] [int] NULL DEFAULT (NULL),
	[legalized] [bit] NOT NULL,
	[elevator] [bit] NOT NULL,
	[sewer] [bit] NOT NULL,
	[intercom] [bit] NOT NULL,
	[phone] [bit] NOT NULL,
	[balcon] [bit] NOT NULL,
	[basement] [bit] NOT NULL,
	[cable_tv] [bit] NOT NULL,
	[aircondition] [bit] NOT NULL,
	[internet] [bit] NOT NULL,
	[parking] [bit] NOT NULL,
	[useljivo] [bit] NOT NULL,
	[new_building] [bit] NOT NULL,
	[under_construction] [bit] NOT NULL,
	[description] [text] NOT NULL,
	PRIMARY KEY CLUSTERED ([id] ASC, [id_source] ASC)
)

ALTER TABLE [dbo].[stanovi_stanovi]  WITH CHECK ADD CONSTRAINT [fk_heating_type_id] FOREIGN KEY([heating_type_id]) REFERENCES [dbo].[stanovi_heating_type] ([id])
ALTER TABLE [dbo].[stanovi_stanovi] CHECK CONSTRAINT [fk_heating_type_id]

ALTER TABLE [dbo].[stanovi_stanovi]  WITH CHECK ADD CONSTRAINT [fk_source_id_source] FOREIGN KEY([id_source]) REFERENCES [dbo].[stanovi_source] ([id])
ALTER TABLE [dbo].[stanovi_stanovi] CHECK CONSTRAINT [fk_source_id_source]
