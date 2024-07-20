#!/usr/bin/perl

use strict;
use warnings;
use LWP::UserAgent;
use HTTP::Request;
use HTTP::Headers;
use YAML::XS 'LoadFile';
use XML::Simple;
use Data::Dumper;

# Load eBay API credentials from YAML configuration file
my $config_path = '/home/robertmcasper/ebay-listing-app/config/ebay.yaml';
my $config = LoadFile($config_path);
my $api_config = $config->{api}{'production.ebay.com'}; # Change to 'sandbox.ebay.com' for testing

# Define the eBay API endpoint for the production environment
my $ebay_api_url = 'https://api.ebay.com/ws/api.dll'; # Ensure correct endpoint

# Create the HTTP headers
my $headers = HTTP::Headers->new(
    'X-EBAY-API-COMPATIBILITY-LEVEL' => $api_config->{compatability},
    'X-EBAY-API-DEV-NAME'            => $api_config->{devid},
    'X-EBAY-API-APP-NAME'            => $api_config->{appid},
    'X-EBAY-API-CERT-NAME'           => $api_config->{certid},
    'X-EBAY-API-CALL-NAME'           => 'AddItem',
    'X-EBAY-API-SITEID'              => $api_config->{siteid},
    'Content-Type'                   => 'text/xml',
    'Accept'                         => 'text/xml'
);

# Define the XML request body
my $request_xml = <<'XML';
<?xml version="1.0" encoding="utf-8"?>
<AddItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>{eBayAuthToken}</eBayAuthToken>
  </RequesterCredentials>
  <Item>
    <Title>Sample Item Title</Title>
    <Description>This is a sample item description.</Description>
    <PrimaryCategory>
      <CategoryID>1234</CategoryID> <!-- Change to your desired category -->
    </PrimaryCategory>
    <StartPrice>9.99</StartPrice>
    <ConditionID>1000</ConditionID>
    <Country>US</Country>
    <Currency>USD</Currency>
    <DispatchTimeMax>3</DispatchTimeMax>
    <ListingDuration>GTC</ListingDuration>
    <ListingType>FixedPriceItem</ListingType>
    <PaymentMethods>PayPal</PaymentMethods>
    <PayPalEmailAddress>robertmcasper\@gmail.com</PayPalEmailAddress>
    <Quantity>1</Quantity>
    <ReturnPolicy>
      <ReturnsAcceptedOption>ReturnsAccepted</ReturnsAcceptedOption>
      <RefundOption>MoneyBack</RefundOption>
      <ReturnsWithinOption>Days_30</ReturnsWithinOption>
      <ShippingCostPaidByOption>Buyer</ShippingCostPaidByOption>
    </ReturnPolicy>
    <ShippingDetails>
      <ShippingType>Flat</ShippingType>
      <ShippingServiceOptions>
        <ShippingServicePriority>1</ShippingServicePriority>
        <ShippingService>USPSMedia</ShippingService>
        <ShippingServiceCost>2.50</ShippingServiceCost>
      </ShippingServiceOptions>
    </ShippingDetails>
  </Item>
</AddItemRequest>
XML

# Replace placeholder with actual token
$request_xml =~ s/\{eBayAuthToken\}/$api_config->{token}/;

# Create the user agent and enable debugging
my $ua = LWP::UserAgent->new;
$ua->add_handler("request_send",  sub { shift->dump; return });
$ua->add_handler("response_done", sub { shift->dump; return });

# Make the API call
my $request = HTTP::Request->new('POST', $ebay_api_url, $headers, $request_xml);
my $response = $ua->request($request);

# Check the response
if ($response->is_success) {
    my $response_xml = $response->decoded_content;
    print "Response:\n$response_xml\n";
    my $xml = XML::Simple->new;
    my $data = $xml->XMLin($response_xml);
    if ($data->{Ack} eq 'Success') {
        print "Item draft created successfully!\n";
    } else {
        print "Error creating item draft: ", Dumper($data->{Errors}), "\n";
    }
} else {
    print "HTTP Error: ", $response->status_line, "\n";
}
