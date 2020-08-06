# Curious Bot Homes
## Project Purpose
Finding the right home at the right price seems to be a lengthy and complicated process. Normally one would go about and view as many properties as possible in order to get an intuition of the property market.

The problem with this approach is that is directly dependent on the buyer's time and not scalable. One first approximation, each viewing may take at least 1.5 hours (including transport). This poses a challenge - one can complete no ore than 2 viewings per day on weekdays and probably 4 in weekends.

If we assume that 100 viewings enough to build a certain intuition of the property market, one would need at least 5 full weeks of dedicated property hunting. This assumption, however, is an order of magnitude below the number of ads published per month. It also does not guarantee informed guess since 100 samples is still insufficient to make a well-informed decision.

The purpose of this project is therefore to make the collection of real estate information automated, scalable and time-independent.

This, in turn will allow the author to:
* Understand the main drivers of real estate prices;
* Build a model that predicts the asking price of real estate;

## Operation
Curious bot homes is a project for collecting real estate data for research purposes.

The target website of this crawler has a paging structure where each page contains several ad tiles. Each tile is clickable and leads to a separate page.

Each tile contains the following elements:
* Image
* Address
* Promotion tag
* Short description
* Square footage
* Price

Curious bot homes crawls over its target site on a schedule specified in `cron.yaml`. The tile elements are extracted, cleaned and saved in a temporary dictionary. Curious bot homes also makes a call to the Google Maps Geocoding API and enriches the extracted data with the geocoding JSON response.

The entire result is then saved to a BigQuery dataset.
