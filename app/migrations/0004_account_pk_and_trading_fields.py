import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0003_media_file"),
    ]

    operations = [
        migrations.RunSQL(
            sql="TRUNCATE TABLE media_files, accounts CASCADE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE media_files DROP COLUMN account_id;

                        ALTER TABLE accounts DROP CONSTRAINT accounts_pkey;
                        ALTER TABLE accounts DROP COLUMN id;
                        ALTER TABLE accounts DROP COLUMN account_number;
                        ALTER TABLE accounts ADD COLUMN id bigint NOT NULL;
                        ALTER TABLE accounts ADD CONSTRAINT accounts_pkey PRIMARY KEY (id);

                        ALTER TABLE media_files ADD COLUMN account_id bigint NOT NULL;
                        ALTER TABLE media_files ADD CONSTRAINT media_files_account_id_fkey
                            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE;

                        ALTER TABLE accounts ADD COLUMN broker varchar(255);
                        ALTER TABLE accounts ADD COLUMN server varchar(255);
                        ALTER TABLE accounts ADD COLUMN currency varchar(10);
                        ALTER TABLE accounts ADD COLUMN leverage integer;
                        ALTER TABLE accounts ADD COLUMN balance numeric(15, 2) NOT NULL DEFAULT 0;
                        ALTER TABLE accounts ADD COLUMN equity numeric(15, 2) NOT NULL DEFAULT 0;
                        ALTER TABLE accounts ADD COLUMN margin numeric(15, 2) NOT NULL DEFAULT 0;
                        ALTER TABLE accounts ADD COLUMN free_margin numeric(15, 2) NOT NULL DEFAULT 0;
                        ALTER TABLE accounts ADD COLUMN profit numeric(15, 2) NOT NULL DEFAULT 0;
                        ALTER TABLE accounts ADD COLUMN margin_level numeric(10, 2) NOT NULL DEFAULT 0;
                    """,
                    reverse_sql=migrations.RunSQL.noop,
                ),
            ],
            state_operations=[
                migrations.RemoveField(model_name="account", name="account_number"),
                migrations.AlterField(
                    model_name="account",
                    name="id",
                    field=models.BigIntegerField(primary_key=True, serialize=False),
                ),
                migrations.AlterField(
                    model_name="mediafile",
                    name="account",
                    field=models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="media_files",
                        to="app.account",
                    ),
                ),
                migrations.AddField(
                    model_name="account",
                    name="broker",
                    field=models.CharField(blank=True, max_length=255, null=True),
                ),
                migrations.AddField(
                    model_name="account",
                    name="server",
                    field=models.CharField(blank=True, max_length=255, null=True),
                ),
                migrations.AddField(
                    model_name="account",
                    name="currency",
                    field=models.CharField(blank=True, max_length=10, null=True),
                ),
                migrations.AddField(
                    model_name="account",
                    name="leverage",
                    field=models.IntegerField(null=True),
                ),
                migrations.AddField(
                    model_name="account",
                    name="balance",
                    field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
                ),
                migrations.AddField(
                    model_name="account",
                    name="equity",
                    field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
                ),
                migrations.AddField(
                    model_name="account",
                    name="margin",
                    field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
                ),
                migrations.AddField(
                    model_name="account",
                    name="free_margin",
                    field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
                ),
                migrations.AddField(
                    model_name="account",
                    name="profit",
                    field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
                ),
                migrations.AddField(
                    model_name="account",
                    name="margin_level",
                    field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
                ),
            ],
        ),
    ]
