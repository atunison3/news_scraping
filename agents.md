# News Scraping Project

## Overview

This project is an ethical web scraper designed to collect news articles from open-source news sites of various organizations, agencies, and government entities. The scraper operates periodically to gather new content and store it in a database for further analysis or dissemination.

## Architecture

The project follows the Onion Architecture pattern, which emphasizes separation of concerns and dependency inversion. The architecture is structured into the following layers:

### Domain Layer
- Contains the core business logic and entities
- `Article` model: Represents a news article with fields such as URL, title, source, publication date, summary, content type, image URL, and tags

### Application Layer (Services)
- Handles business logic and use cases
- Orchestrates interactions between domain entities and external interfaces

### Infrastructure Layer (Repositories)
- Manages data persistence and external service integrations
- Currently configured to use SQLite database for storing articles

## Key Features

- **Ethical Scraping**: Respects robots.txt and implements rate limiting to avoid overloading source websites
- **Periodic Execution**: Designed to run on a schedule to collect new articles regularly
- **Database Integration**: Stores scraped articles in a structured SQLite database
- **Modular Design**: Onion architecture allows for easy testing, maintenance, and extension

## Target Sources

The scraper targets news sites from:

- **Business Organizations**: Apple, Boeing, Lockheed Martin, Microsoft, Nvidia, Raytheon, SpaceX, Textron
- **US Government Agencies**: Department of Homeland Security, Department of Defense, US Army, US Marine Corps, US Navy, US Air Force, US Space Force, US Coast Guard, National Guard, NOAA
- **State Agencies**: Texas Department of Public Safety

## Database Schema

The project uses SQLite with a schema that supports article storage with proper indexing and foreign key constraints.

## Usage

The main entry point is `src/main.py`, which handles database initialization and connection management.