#!/usr/bin/perl

use strict;
use warnings;
use Net::eBay;
use YAML::XS 'LoadFile';
use Getopt::Long;

# Load configuration
my $config_file = '/home/robertmcasper/ebay-listing-app/config/ebay.yaml';
my $config = LoadFile($config_file)->{api}->{'production.ebay.com'};

# Check if required config values are defined
unless ($config->{SiteLevel}) {
    die "Error: SiteLevel must be defined in the configuration file.\n";
}

# Get input parameters
my ($title, $description, $category_id, $start_price, $condition_id, $picture_url, $quantity, %item_specifics);
GetOptions(
    'title=s' => \$title,
    'description=s' => \$description,
    'category_id=i' => \$category_id,
    'start_price=f' => \$start_price,
    'condition_id=i' => \$condition_id,
    'picture_url=s' => \$picture_url,
    'quantity=i' => \$quantity,
    'item_specifics=s%' => \%item_specifics,
);

# Check required parameters
unless ($title && $description && $category_id && $start_price && $condition_id && $picture_url && $quantity) {
    die "Usage: $0 --title <title> --description <description> --category_id <category_id> --start_price <price> --condition_id <condition_id> --picture_url <url> --quantity <quantity> [--item_specifics <name=value>]\n";
}

# Initialize eBay API
my $eBay = Net::eBay->new({
    appid  => $config->{appid},
    certid => $config->{certid},
    devid  => $config->{devid},
    token  => $config->{token},
    siteid => $config->{siteid},
    compatibility_level => 967,
    apiurl => 'https://api.ebay.com/ws/api.dll',
    SiteLevel => $config->{SiteLevel},
    debug  => 1
});

# Check if eBay object is defined
unless ($eBay) {
    die "Error initializing Net::eBay object.\n";
}

# Define item specifics
my @item_specifics_array;
while (my ($name, $value) = each %item_specifics) {
    push @item_specifics_array, { Name => $name, Value => $value };
}

# Define the item to be listed
my %item = (
    Title => $title,
    Description => $description,
    PrimaryCategory => { CategoryID => $category_id },
    StartPrice => $start_price,
    ConditionID => $condition_id,
    Country => 'US',
    Currency => 'USD',
    DispatchTimeMax => 3,
    ListingDuration => 'Days_7',
    ListingType => 'FixedPriceItem',
    PaymentMethods => 'PayPal',
    PayPalEmailAddress => $config->{PayPalEmailAddress},
    PictureDetails => {
        PictureURL => $picture_url,
    },
    PostalCode => '95125',
    Quantity => $quantity,
    ItemSpecifics => { NameValueList => \@item_specifics_array },
    ReturnPolicy => {
        ReturnsAcceptedOption => 'ReturnsAccepted',
        RefundOption => 'MoneyBack',
        ReturnsWithinOption => 'Days_30',
        ShippingCostPaidByOption => 'Buyer'
    },
    ShippingDetails => {
        ShippingType => 'Flat',
        ShippingServiceOptions => {
            ShippingServicePriority => 1,
            ShippingService => 'USPSMedia',
            ShippingServiceCost => '2.50'
        }
    },
    Site => $config->{Site}
);

# Create the listing draft
my $response = $eBay->submitRequest('AddItem', \%item);

# Check the response
if ($response->{Ack} eq 'Success') {
    print "Item listed successfully. Item ID: $response->{ItemID}\n";
} else {
    foreach my $error (@{$response->{Errors}}) {
        print "Error: $error->{LongMessage}\n";
    }
}
