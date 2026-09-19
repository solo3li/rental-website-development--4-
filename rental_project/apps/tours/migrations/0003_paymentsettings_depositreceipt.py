import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tours', '0002_tourbooking_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deposit_required', models.BooleanField(default=True, verbose_name='تفعيل إلزامية دفع العربون')),
                ('deposit_amount_egp', models.IntegerField(default=100, verbose_name='قيمة العربون الثابت (ج.م)')),
                ('instapay_address', models.CharField(default='cairo.students@instapay', max_length=100, verbose_name='عنوان InstaPay (IPA)')),
                ('instapay_account_name', models.CharField(default='سكن طلاب القاهرة', max_length=100, verbose_name='اسم المستفيد في InstaPay')),
                ('vodafone_cash_number', models.CharField(default='01012345678', max_length=50, verbose_name='رقم فودافون كاش')),
                ('orange_cash_number', models.CharField(blank=True, default='01212345678', max_length=50, null=True, verbose_name='رقم محفظة بديلة (أورنج/اتصالات/وي)')),
                ('payment_instructions', models.TextField(blank=True, default='برجاء تحويل مبلغ العربون لتأكيد جدية المعاينة وحجز الموعد، ثم رفع لقطة الشاشة (Screenshot) للتأكيد.', null=True, verbose_name='تعليمات الدفع المعروضة للطالب')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Payment Setting',
                'verbose_name_plural': 'Payment Settings',
            },
        ),
        migrations.AlterField(
            model_name='tourbooking',
            name='status',
            field=models.CharField(choices=[('confirmed', 'Confirmed'), ('pending', 'Pending'), ('completed', 'Completed'), ('cancelled', 'Cancelled'), ('rejected', 'Rejected')], default='pending', max_length=20),
        ),
        migrations.CreateModel(
            name='DepositReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField(default=100, verbose_name='مبلغ العربون (ج.م)')),
                ('payment_method', models.CharField(choices=[('instapay', 'InstaPay (إنستاباي)'), ('vodafone_cash', 'Vodafone Cash (فودافون كاش)'), ('orange_cash', 'Orange Cash (أورنج كاش)'), ('etisalat_cash', 'Etisalat Cash (اتصالات كاش)'), ('we_pay', 'WE Pay (وي باي)'), ('smart_wallet', 'المحافظ البنكية الذكية'), ('other', 'طريقة أخرى')], default='instapay', max_length=50, verbose_name='وسيلة الدفع')),
                ('sender_info', models.CharField(blank=True, max_length=100, null=True, verbose_name='رقم المحفظة / اسم المحول')),
                ('reference_number', models.CharField(blank=True, max_length=100, null=True, verbose_name='الرقم المرجعي للعملية')),
                ('receipt_image', models.ImageField(upload_to='receipts/%Y/%m/', verbose_name='صورة إيصال التحويل (Screenshot)')),
                ('status', models.CharField(choices=[('pending', 'قيد المراجعة ⏳'), ('approved', 'معتمد ومقبول ✅'), ('rejected', 'مرفوض ❌')], default='pending', max_length=20, verbose_name='حالة المراجعة')),
                ('rejection_reason', models.TextField(blank=True, null=True, verbose_name='سبب الرفض')),
                ('reviewed_at', models.DateTimeField(blank=True, null=True, verbose_name='وقت المراجعة')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الرفع')),
                ('booking', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='deposit_receipt', to='tours.tourbooking', verbose_name='طلب المعاينة / الحجز')),
                ('reviewed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_receipts', to=settings.AUTH_USER_MODEL, verbose_name='المشرف المراجع')),
            ],
            options={
                'verbose_name': 'Deposit Receipt',
                'verbose_name_plural': 'Deposit Receipts',
                'ordering': ['-created_at'],
            },
        ),
    ]
