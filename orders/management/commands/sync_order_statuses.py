from django.core.management.base import BaseCommand
from django.utils import timezone
from orders.models import Order, OrderItem

class Command(BaseCommand):
    help = 'Synchronize order statuses with their item statuses'

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

        # Find orders where status doesn't match item statuses
        mismatched_orders = []

        for order in Order.objects.all():
            item_statuses = list(order.items.values_list('status', flat=True))

            # If order status doesn't match any item status, it needs syncing
            if item_statuses and order.status not in item_statuses:
                # All items should match the order status
                mismatched_orders.append({
                    'order': order,
                    'order_status': order.status,
                    'item_statuses': item_statuses
                })

        if not mismatched_orders:
            self.stdout.write(self.style.SUCCESS('No mismatched statuses found!'))
            return

        self.stdout.write(f'Found {len(mismatched_orders)} orders with mismatched statuses:')

        for mismatch in mismatched_orders:
            order = mismatch['order']
            order_status = mismatch['order_status']
            item_statuses = mismatch['item_statuses']

            self.stdout.write(
                f'Order #{str(order.id)[:8]} - Order: {order_status}, Items: {set(item_statuses)}'
            )

            if not dry_run:
                # Update all items to match order status
                updated_count = order.items.update(status=order_status)

                # Update timestamps if needed
                if order_status == 'confirmed' and not order.confirmed_at:
                    order.confirmed_at = timezone.now()
                    order.save(update_fields=['confirmed_at'])
                elif order_status == 'ready' and not order.ready_at:
                    order.ready_at = timezone.now()
                    order.save(update_fields=['ready_at'])
                elif order_status == 'delivered' and not order.delivered_at:
                    order.delivered_at = timezone.now()
                    order.save(update_fields=['delivered_at'])

                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Updated {updated_count} items to {order_status}')
                )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'Would update {len(mismatched_orders)} orders. Run without --dry-run to apply changes.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully synced {len(mismatched_orders)} orders!')
            )
