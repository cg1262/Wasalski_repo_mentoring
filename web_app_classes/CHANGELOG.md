# Changelog

All notable changes to the Web App Classes project will be documented in this file.

## [v2.0 - In Development] 🚧

### Goal: Zero Frontend Bugs
**Objective: Eliminate all visual glitches and UI inconsistencies for a polished user experience.**

### Fixed in v2.0
- **Sticky Header Z-Index Issue**: Fixed table rows appearing to scroll through headers
  - Improved table border management and spacing
  - Fixed container padding and table structure
  - Enhanced border separation between header and body

### Added in v2.0
- **Data Analysis Buttons**: Advanced statistical analysis tools
  - **Statistics Button**: Shows column statistics (count, min, max, average, unique values)
  - **Describe Button**: Pandas-style describe function with quartiles and standard deviation
  - **Data Types Button**: Automatic data type detection (numeric, string, datetime, boolean)
  - **Modal Display**: Professional table layout for analysis results
  - **Smart Analysis**: Handles both numeric and categorical data appropriately

### Technical Improvements
- Enhanced button grouping with Bootstrap btn-group
- Added comprehensive statistical calculations
- Implemented percentile calculations for quartiles
- Added data type inference algorithms
- Created reusable modal system for analysis display

### Known Issues to Fix
- [ ] Cross-browser compatibility testing
- [ ] Mobile responsiveness improvements
- [ ] Performance optimizations for large datasets

---

## [v1.0] - 2025-07-10 🎉

### Major Release - Feature Complete
**Web App Classes has reached v1.0 with a comprehensive set of features for dynamic endpoint data exploration.**

### Core Features
- **Dynamic Method Discovery**: Automatically loads and discovers Python class methods from endpoint files
- **Interactive Data Tables**: Full-featured data visualization with filtering and sorting
- **Real-time Processing**: Execute API methods and view results instantly
- **Cancellable Operations**: Interrupt long-running processes with cancel button
- **Data Export**: Download results as CSV or view as JSON

### Table Features (Data Wrangler Style)
- **Advanced Sorting**: Click headers to sort ascending/descending with smart type detection
- **Real-time Filtering**: Filter inputs in each column header
- **Sticky Headers**: Headers remain visible while scrolling through data
- **Visual Indicators**: Sort direction arrows (▲▼↕) and hover effects
- **Multi-column Filtering**: Apply multiple filters simultaneously
- **Performance Optimized**: Handles large datasets efficiently

### User Experience
- **Professional UI**: Modern Bootstrap design with gradient styling
- **Responsive Layout**: Works on different screen sizes
- **Error Handling**: Comprehensive error display with stack traces
- **Progress Feedback**: Loading indicators and execution counters
- **Method Management**: Reload endpoints without restarting application

### Technical Architecture
- **Flask Backend**: Python web framework with dynamic module loading
- **Class Introspection**: Uses Python inspect module for method discovery
- **Pandas Integration**: Seamless DataFrame handling and conversion
- **Modern Frontend**: ES6 JavaScript with AbortController for cancellation
- **CSS Grid/Flexbox**: Responsive layout system

### Security
- **Defensive Focus**: Designed for security analysis and defensive tools only
- **Safe Execution**: Controlled environment for running endpoint methods
- **Error Isolation**: Proper exception handling prevents system crashes

---

## Previous Versions

### [v0.04] - 2025-07-10
- Added table filtering and sorting (Data Wrangler style)
- Interactive column headers with filter inputs
- Smart numeric and string sorting with visual indicators

---

## [v0.03] - 2025-07-10

### Added
- **Sticky Table Headers**
  - Table headers now remain fixed at the top when scrolling through data
  - Added shadow effect to sticky headers for better visual separation
  - Improved readability for large datasets

### Changed
- **Table Display Enhancement**
  - Headers stay visible while scrolling through table data
  - Better user experience when viewing large datasets
  - Consistent header visibility regardless of table size

### Technical Details
- Added CSS `position: sticky` to table headers
- Set `top: 0` and `z-index: 10` for proper positioning
- Added `box-shadow` for visual depth
- Ensured background color consistency with `!important` flag

---

## [v0.02] - 2025-07-10

### Added
- **Cancel Button for Long-Running Operations**
  - Added red "Anuluj" (Cancel) button in the loading section
  - Implemented AbortController for HTTP request cancellation
  - Added proper error handling for cancelled operations
  - Users can now interrupt long-running API calls (like Checkmarx requests)

### Changed
- **Enhanced User Experience**
  - Loading section now includes cancel functionality
  - Improved error messages for cancelled operations
  - Better handling of interrupted processes

### Technical Details
- Added `abortController` global variable to track ongoing requests
- Modified `executeMethod()` function to use AbortController signal
- Added `cancelExecution()` function to handle cancellation
- Updated error handling to differentiate between cancellation and network errors

---

## [v0.01] - 2025-07-10

### Fixed
- **Method Detection Issue**
  - Fixed `_extract_methods_from_class` method in `app.py:82`
  - Changed `inspect.ismethod` to `inspect.isfunction` for proper method detection
  - Removed redundant static method detection logic that was causing conflicts

### Technical Details
- **File:** `/Users/mateusz/Desktop/web_app_classes/app.py`
- **Line 82:** Changed method detection from `inspect.ismethod` to `inspect.isfunction`
- **Lines 95-107:** Removed duplicate static method detection code
- **Issue:** Methods were not being properly detected, causing "missing 1 required positional argument: 'self'" errors

### Root Cause
The original code was trying to extract methods using `inspect.ismethod` which only works for bound methods on class instances, not unbound methods on class definitions. This caused the `get_applications` and `get_scans` methods from the CheckmarxAPI class to not be detected properly.

### Impact
- ✅ `get_applications` method now works correctly
- ✅ `get_scans` method now works correctly
- ✅ All class methods are properly detected and executable
- ✅ No more "missing self argument" errors