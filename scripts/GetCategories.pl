#!/usr/bin/perl
use strict;
use warnings;
use YAML::XS 'LoadFile';
use LWP::UserAgent;
use HTTP::Request;
use HTTP::Headers;

my $config = LoadFile('/home/robertmcasper/ebay-listing-app/config/ebay.yaml')->{api}{sandbox}{ebay};

# Define eBay API credentials
my $appid = $config->{appid};
my $dev_name = $config->{devid};
my $cert_name = $config->{certid};
my $auth_token = $config->{token};
my $compatibility = $config->{compatability};
my $siteid = $config->{siteid};
my $endpoint = "https://api.sandbox.ebay.com/wsapi";

# Construct the URL with query parameters
my $url = "$endpoint?callname=GetCategories&siteid=$siteid&appid=$appid&version=$compatibility&Routing=new";

# Define the SOAP request
my $soap_request = <<"END_SOAP";
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns="urn:ebay:apis:eBLBaseComponents">
  <soap:Header>
    <RequesterCredentials>
      <eBayAuthToken>$auth_token</eBayAuthToken>
    </RequesterCredentials>
  </soap:Header>
  <soap:Body>
    <GetCategoriesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
      <CategorySiteID>$siteid</CategorySiteID>
      <ViewAllNodes>true</ViewAllNodes>
    </GetCategoriesRequest>
  </soap:Body>
</soap:Envelope>
END_SOAP

# Make the SOAP call
my $objHeader = HTTP::Headers->new;
$objHeader->push_header('Content-Type' => 'text/xml');
my $objRequest = HTTP::Request->new(
  "POST",
  $url,
  $objHeader,
  $soap_request
);

# Handle the response
my $objUserAgent = LWP::UserAgent->new;
my $objResponse = $objUserAgent->request($objRequest);

if (!$objResponse->is_error) {
  print $objResponse->content;
} else {
  print $objResponse->error_as_HTML;
}
