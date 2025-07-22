from django.core.management.base import BaseCommand
from django.utils import timezone
from orders.models import Order, OrderItem

class Command(BaseCommand):
    help = 'Check order status timestamps and update missing ones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        # Note: Items no longer have individual status - only orders have status
        self.stdout.write(self.style.SUCCESS('Items no longer have individual status.'))
        self.stdout.write('Only orders have status. Items implicitly follow their parent order status.')

        # Find orders with missing timestamps
        orders_needing_timestamps = []

        for order in Order.objects.all():
            needs_update = False
            missing_timestamps = []

            if order.status == 'confirmed' and not order.confirmed_at:
                needs_update = True
                missing_timestamps.append('confirmed_at')

            if order.status == 'ready' and not order.ready_at:
                needs_update = True
                missing_timestamps.append('ready_at')

            if order.status == 'delivered' and not order.delivered_at:
                needs_update = True
                missing_timestamps.append('delivered_at')

            if needs_update:
                orders_needing_timestamps.append({
                    'order': order,
                    'missing_timestamps': missing_timestamps
                })

        if not orders_needing_timestamps:
            self.stdout.write(self.style.SUCCESS('All order timestamps are properly set!'))
            return

        self.stdout.write(f'Found {len(orders_needing_timestamps)} orders with missing timestamps:')

        for item in orders_needing_timestamps:
            order = item['order']
            missing = item['missing_timestamps']

            self.stdout.write(
                f'Order #{str(order.id)[:8]} - Status: {order.status}, Missing: {", ".join(missing)}'
            )

            if not dry_run:
                now = timezone.now()
                updates = {}

                if 'confirmed_at' in missing:
                    order.confirmed_at = now
                    updates['confirmed_at'] = now

                if 'ready_at' in missing:
                    order.ready_at = now
                    updates['ready_at'] = now

                if 'delivered_at' in missing:
                    order.delivered_at = now
                    updates['delivered_at'] = now

                if updates:
                    order.save(update_fields=list(updates.keys()))
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Updated timestamps: {", ".join(updates.keys())}')
                    )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'Would update {len(orders_needing_timestamps)} orders. Run without --dry-run to apply changes.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated timestamps for {len(orders_needing_timestamps)} orders!')
            )
