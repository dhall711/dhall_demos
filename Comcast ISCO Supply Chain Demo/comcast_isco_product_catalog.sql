-- ============================================================================
-- Comcast ISCO - Product Catalog (Standalone DDL + Load)
-- This script isolates the PRODUCT_CATALOG table creation and data load so
-- the rest of the main setup can run independently.
-- ============================================================================

USE DATABASE ISCO_ANALYTICS;
USE SCHEMA PROD;

-- ============================================================================
-- PRODUCT_CATALOG Table (Rich Text Content for Cortex Search)
-- ============================================================================

CREATE OR REPLACE TABLE PRODUCT_CATALOG (
    CATALOG_ID VARCHAR(50) NOT NULL,
    PRODUCT_SKU VARCHAR(30) NOT NULL,
    SUPPLIER_ID VARCHAR(20) NOT NULL,
    PRODUCT_NAME VARCHAR(200) NOT NULL,
    PRODUCT_DESCRIPTION TEXT NOT NULL,
    TECHNICAL_SPECIFICATIONS TEXT NOT NULL,
    VENDOR_OVERVIEW TEXT NOT NULL,
    INSTALLATION_GUIDE TEXT NOT NULL,
    COMPATIBILITY_NOTES TEXT NOT NULL,
    FEATURE_HIGHLIGHTS TEXT NOT NULL,
    MARKET_POSITIONING TEXT NOT NULL,
    CUSTOMER_USE_CASES TEXT NOT NULL,
    COMPETITIVE_ADVANTAGES TEXT NOT NULL,
    CERTIFICATION_COMPLIANCE TEXT NOT NULL,
    PRODUCT_IMAGE_URL VARCHAR(500),
    PRODUCT_IMAGE_ALT_TEXT TEXT,
    ADDITIONAL_IMAGES VARIANT,
    IMAGE_CLASSIFICATION_TAGS VARIANT,
    PRODUCT_DOCUMENTATION_URLS VARIANT,
    CREATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_DATE TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert Product Catalog Data with Rich Text and Image Metadata
INSERT INTO PRODUCT_CATALOG 
SELECT
'CAT_001', 'SKU_CM001', 'SUP_001', 'Arris SURFboard SB8200 DOCSIS 3.1 Cable Modem',
'The Arris SURFboard SB8200 is a high-performance DOCSIS 3.1 cable modem designed for next-generation broadband services. This advanced modem delivers ultra-fast internet speeds up to 2 Gbps, making it perfect for households with multiple connected devices, 4K streaming, online gaming, and smart home applications. The SB8200 features dual Gigabit Ethernet ports for maximum flexibility and supports both IPv4 and IPv6 protocols for future network compatibility.',
'DOCSIS 3.1 technology with 32x8 channel bonding, dual 1 Gigabit Ethernet ports, supports speeds up to 2 Gbps download and 200 Mbps upload, Broadcom BCM3390 chipset, 1024-QAM and OFDM/OFDMA support, active queue management for reduced latency, IPv4 and IPv6 dual stack support, dimensions 7.0 x 5.0 x 1.75 inches, operating temperature 32°F to 104°F.',
'Arris International is a global leader in entertainment and communications technology, serving broadband operators worldwide. With decades of experience in cable infrastructure, Arris provides innovative solutions that enable service providers to deliver next-generation services. The company specializes in DOCSIS technology, fiber optics, and network management solutions. Arris has a strong partnership with Comcast, providing reliable equipment that meets stringent performance and compatibility requirements.',
'Installation is straightforward with step-by-step guidance. Connect coaxial cable from wall outlet to modem, connect Ethernet cable from modem to router or device, plug in power adapter and wait for LED indicators to show solid connectivity. The modem includes self-provisioning capabilities that automatically configure optimal settings. Professional installation support is available for complex network setups.',
'Compatible with major cable internet providers including Comcast Xfinity, Cox, Spectrum, and Mediacom. Not compatible with DSL, fiber, or satellite internet services. Requires DOCSIS 3.1 service plan for optimal performance. Works seamlessly with all router brands and WiFi systems. Supports Windows, macOS, Linux operating systems.',
'Advanced DOCSIS 3.1 technology, ultra-low latency for gaming and video calls, energy-efficient design with intelligent power management, robust security protocols, easy setup with mobile app support, reliable 24/7 performance, future-ready technology investment, superior signal processing for consistent speeds.',
'Positioned as premium cable modem solution for power users and households with high bandwidth demands. Target market includes cord-cutters, gamers, remote workers, and smart home enthusiasts. Competes with Netgear CM1000 and Motorola MB8600 in high-performance segment.',
'Ideal for households with 10+ connected devices, 4K/8K video streaming, cloud gaming, video conferencing, smart home automation, home office setups, content creators, and tech enthusiasts requiring maximum internet performance.',
'Offers superior performance-to-price ratio compared to competitors, advanced chipset technology, proven reliability in Comcast network, excellent customer support, comprehensive warranty coverage, and future upgrade path compatibility.',
'FCC certified, DOCSIS 3.1 specification compliant, Energy Star qualified, RoHS compliant for environmental standards, UL listed for safety, meets Comcast technical requirements and compatibility standards.',
'https://images.comcast.com/products/modems/arris-sb8200-front-view.jpg',
'Arris SURFboard SB8200 DOCSIS 3.1 cable modem in white, front view showing LED status indicators, coaxial input, dual ethernet ports, and power connection. Compact rectangular design with ventilation grilles and Arris branding.',
PARSE_JSON('["https://images.comcast.com/products/modems/arris-sb8200-back-view.jpg", "https://images.comcast.com/products/modems/arris-sb8200-side-profile.jpg", "https://images.comcast.com/products/modems/arris-sb8200-led-status.jpg", "https://images.comcast.com/products/modems/arris-sb8200-packaging.jpg"]'),
PARSE_JSON('["cable modem", "white device", "rectangular shape", "LED indicators", "ethernet ports", "coaxial connector", "compact design", "ventilation grilles", "networking equipment", "broadband device"]'),
PARSE_JSON('["https://docs.comcast.com/products/arris-sb8200-installation-guide.pdf", "https://docs.comcast.com/products/arris-sb8200-user-manual.pdf", "https://docs.comcast.com/products/arris-sb8200-quick-start.pdf"]'),
CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()

UNION ALL SELECT
'CAT_002', 'SKU_STB001', 'SUP_002', 'Technicolor XiOne X1 DVR Set-Top Box',
'The Technicolor XiOne represents the pinnacle of entertainment technology, combining advanced 4K Ultra HD capabilities with cloud DVR functionality and voice control integration. This next-generation set-top box delivers seamless access to live TV, on-demand content, streaming apps, and personal recordings through an intuitive interface powered by machine learning and artificial intelligence.',
'4K Ultra HD video output with HDR10 support, 1TB internal storage for DVR recordings, 6-tuner capability for simultaneous recording and viewing, Dolby Atmos audio support, 802.11ac WiFi and Gigabit Ethernet connectivity, Bluetooth for wireless accessories, voice remote with Xfinity Voice Remote capabilities, Android TV platform with Google Assistant integration.',
'Technicolor Connected Home leverages over 100 years of innovation in entertainment technology to deliver cutting-edge set-top boxes and media devices. As a trusted Comcast partner, Technicolor provides robust, feature-rich solutions that enhance the viewer experience while ensuring reliable performance and seamless integration with Xfinity services.',
'Professional installation includes optimal placement for signal reception, WiFi connectivity setup, voice remote pairing, and customer training on advanced features. Device supports both coaxial and IP delivery for maximum flexibility.',
'Exclusive compatibility with Xfinity X1 platform, supports Xfinity Flex streaming service, integrates with Xfinity Home security system, compatible with Xfinity Mobile for seamless device integration.',
'Industry-leading 4K HDR picture quality, cloud DVR with unlimited storage options, voice control and search capabilities, comprehensive streaming app ecosystem, personalized content recommendations, multi-room viewing support.',
'Premium entertainment solution targeting cord-cutters and traditional TV viewers seeking advanced features. Competes with Apple TV 4K, Roku Ultra, and Amazon Fire TV Cube in the premium streaming device market.',
'Ideal for entertainment enthusiasts, families with diverse viewing preferences, cord-cutters maintaining some live TV, users seeking voice control convenience, households with multiple TVs requiring synchronized experience.',
'Superior integration with Comcast services, advanced AI-powered recommendations, comprehensive app ecosystem, professional installation and support, unlimited cloud DVR capabilities, seamless multi-device experience.',
'FCC certified, Dolby certified, Android TV certified, Energy Star compliant, meets all broadcast and streaming technical standards.',
'https://images.comcast.com/products/settop/technicolor-xione-front-angle.jpg',
'Technicolor XiOne X1 DVR set-top box in sleek black design, front three-quarter view showing curved edges, LED display panel, ventilation slots, and modern minimalist aesthetic with Xfinity branding.',
PARSE_JSON('["https://images.comcast.com/products/settop/technicolor-xione-remote.jpg", "https://images.comcast.com/products/settop/technicolor-xione-back-ports.jpg", "https://images.comcast.com/products/settop/technicolor-xione-ui-screenshot.jpg", "https://images.comcast.com/products/settop/technicolor-xione-setup.jpg"]'),
PARSE_JSON('["set-top box", "black device", "curved design", "LED display", "entertainment device", "streaming box", "DVR recorder", "TV equipment", "modern design", "media player"]'),
PARSE_JSON('["https://docs.comcast.com/products/technicolor-xione-user-guide.pdf", "https://docs.comcast.com/products/x1-platform-features.pdf", "https://docs.comcast.com/products/voice-remote-guide.pdf"]'),
CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()

UNION ALL SELECT
'CAT_003', 'SKU_RTR001', 'SUP_003', 'Cisco Meraki MX68 Security Appliance',
'The Cisco Meraki MX68 is an enterprise-grade security appliance designed for small to medium businesses requiring advanced network security, SD-WAN capabilities, and simplified management. This cloud-managed solution provides comprehensive threat protection, content filtering, and network optimization while maintaining ease of deployment and operation.',
'Advanced threat protection with intrusion detection and prevention, content filtering and web security, SD-WAN capabilities with automatic failover, cloud-based management and monitoring, 250 Mbps firewall throughput, 8 Gigabit Ethernet ports, dual WAN support for redundancy, integration with Meraki ecosystem.',
'Cisco Systems leads the networking industry with innovative solutions that secure and connect businesses worldwide. The Meraki division specializes in cloud-managed networking solutions that simplify enterprise IT while providing enterprise-grade security and performance. Cisco maintains a strategic partnership with Comcast for business internet services.',
'Zero-touch provisioning enables remote deployment and configuration. Cloud-based dashboard provides centralized management of all network functions. Professional services available for complex network integration and migration projects.',
'Optimized for Comcast Business Internet services, supports Comcast managed network services, integrates with Comcast security solutions, compatible with Comcast Business Voice over IP systems.',
'Cloud-managed simplicity, enterprise-grade security, SD-WAN optimization, automatic threat updates, comprehensive reporting and analytics, scalable architecture, remote troubleshooting capabilities.',
'Premium business networking solution targeting growing businesses requiring enterprise features with simplified management. Competes with SonicWall, Fortinet, and Palo Alto Networks in SMB security market.',
'Ideal for small businesses, remote offices, retail locations, healthcare practices, professional services firms, and any organization requiring robust security with simple management.',
'Cloud management eliminates on-site IT complexity, automatic security updates, comprehensive threat protection, proven enterprise reliability, seamless scalability, professional support services.',
'FCC certified, meets enterprise security standards, compliant with healthcare and financial regulations, Cisco security certifications.',
'https://images.comcast.com/products/networking/cisco-meraki-mx68-front.jpg',
'Cisco Meraki MX68 security appliance in charcoal gray, professional front view displaying multiple ethernet ports, status LEDs, rack-mount ears, and industrial design suitable for business environments with Cisco Meraki branding.',
PARSE_JSON('["https://images.comcast.com/products/networking/cisco-meraki-mx68-back.jpg", "https://images.comcast.com/products/networking/cisco-meraki-mx68-dashboard.jpg", "https://images.comcast.com/products/networking/cisco-meraki-mx68-rack-mount.jpg", "https://images.comcast.com/products/networking/cisco-meraki-topology.jpg"]'),
PARSE_JSON('["security appliance", "gray device", "rack mountable", "ethernet ports", "business equipment", "networking hardware", "firewall device", "industrial design", "LED indicators", "enterprise router"]'),
PARSE_JSON('["https://docs.comcast.com/products/cisco-meraki-mx68-admin-guide.pdf", "https://docs.comcast.com/products/meraki-dashboard-guide.pdf", "https://docs.comcast.com/products/sd-wan-configuration.pdf"]'),
CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()

UNION ALL SELECT
'CAT_004', 'SKU_FBER001', 'SUP_005', 'Nokia Optical Network Terminal (ONT)',
'The Nokia ONT delivers fiber-to-the-home (FTTH) connectivity with support for gigabit internet speeds, multiple service delivery, and future-ready technology. This optical network terminal provides the critical interface between fiber optic infrastructure and customer premises equipment, enabling next-generation broadband services.',
'GPON and XGS-PON technology support, up to 10 Gbps downstream capability, multiple Gigabit Ethernet ports, integrated WiFi 6 option, voice service support, battery backup capability, remote management and diagnostics, compact wall-mount design.',
'Nokia Corporation brings decades of telecommunications expertise to fiber optic solutions, providing reliable and innovative products that enable service providers to deliver ultra-high-speed broadband services. Nokia maintains strong partnerships with major operators including Comcast for fiber network deployments.',
'Professional fiber installation required with specialized optical equipment. Device supports remote provisioning and configuration. Comprehensive testing and certification process ensures optimal performance.',
'Designed for Comcast fiber network architecture, supports Comcast business and residential fiber services, compatible with Xfinity services over fiber infrastructure.',
'Gigabit-plus internet speeds, future-ready fiber technology, multiple service support, battery backup for voice services, professional installation and support, environmental hardening.',
'Premium fiber solution for high-speed internet markets. Targets areas with fiber infrastructure requiring maximum performance and reliability.',
'Perfect for bandwidth-intensive users, businesses requiring guaranteed speeds, areas with new fiber infrastructure, customers seeking future-proof connectivity solutions.',
'Industry-leading fiber technology, Nokia reliability and support, seamless Comcast service integration, professional installation, comprehensive warranty coverage.',
'Telecom grade certifications, fiber optic standards compliant, environmental and safety certifications.',
'https://images.comcast.com/products/fiber/nokia-ont-wall-mount.jpg',
'Nokia Optical Network Terminal (ONT) in white, wall-mounted configuration showing fiber optic input, ethernet ports, power connection, status indicator lights, and compact design optimized for residential installation.',
PARSE_JSON('["https://images.comcast.com/products/fiber/nokia-ont-fiber-connection.jpg", "https://images.comcast.com/products/fiber/nokia-ont-installation-kit.jpg", "https://images.comcast.com/products/fiber/nokia-ont-status-lights.jpg", "https://images.comcast.com/products/fiber/fiber-network-diagram.jpg"]'),
PARSE_JSON('["fiber terminal", "white device", "wall mounted", "optical equipment", "ethernet ports", "fiber input", "status lights", "compact design", "telecommunications equipment", "broadband terminal"]'),
PARSE_JSON('["https://docs.comcast.com/products/nokia-ont-installation-guide.pdf", "https://docs.comcast.com/products/fiber-service-manual.pdf", "https://docs.comcast.com/products/gpon-technology-overview.pdf"]'),
CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()

UNION ALL SELECT
'CAT_005', 'SKU_INST001', 'SUP_010', 'Comcast Self-Install Kit - Basic',
'The Comcast Self-Install Kit provides everything customers need to quickly and easily set up their internet service without a technician visit. This comprehensive kit includes all necessary cables, adapters, and step-by-step instructions with QR code access to video tutorials and live chat support.',
'Includes coaxial cables, Ethernet cable, cable splitter, power adapter, comprehensive instruction manual with multilingual support, QR codes linking to video tutorials, access to 24/7 chat support during installation, activation instructions, troubleshooting guide.',
'FedEx Supply Chain manages the logistics and fulfillment of Comcast self-install kits, ensuring rapid delivery and complete kit accuracy. This partnership leverages FedEx expertise in complex logistics to deliver seamless customer experiences.',
'Designed for customer self-installation with clear visual instructions and digital support resources. Average installation time is 15-30 minutes with step-by-step guidance.',
'Specifically designed for Comcast Xfinity internet services, compatible with all Comcast-approved modems and equipment, supports standard residential installations.',
'No technician appointment required, same-day service activation possible, cost-effective installation option, comprehensive support resources, quality components ensure reliable connection.',
'Entry-level self-service option targeting tech-comfortable customers and basic internet service installations.',
'Perfect for tech-savvy customers, apartment dwellers, customers with existing cable infrastructure, users seeking immediate service activation.',
'Eliminates installation delays, reduces service costs, provides installation flexibility, includes comprehensive support resources, uses quality components for reliability.',
'All components meet Comcast technical standards and industry safety requirements.',
'https://images.comcast.com/products/kits/self-install-kit-contents.jpg',
'Comcast Self-Install Kit contents laid out on white background, showing coaxial cables, ethernet cable, cable splitter, power adapter, instruction booklet with Xfinity branding, and QR code cards for digital support.',
PARSE_JSON('["https://images.comcast.com/products/kits/self-install-kit-box.jpg", "https://images.comcast.com/products/kits/installation-diagram.jpg", "https://images.comcast.com/products/kits/qr-code-tutorial.jpg", "https://images.comcast.com/products/kits/cable-connection-guide.jpg"]'),
PARSE_JSON('["installation kit", "cables and adapters", "instruction manual", "QR codes", "coaxial cables", "ethernet cable", "splitter", "power adapter", "packaging materials", "self-service kit"]'),
PARSE_JSON('["https://docs.comcast.com/products/self-install-guide.pdf", "https://docs.comcast.com/products/installation-troubleshooting.pdf", "https://docs.comcast.com/products/activation-instructions.pdf"]'),
CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP();


