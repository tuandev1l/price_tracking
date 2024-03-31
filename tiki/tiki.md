- get categories
- get list of products
  SCHEMA:

0. COMMON:

- ecommerce: TIKI
  - original_id: INT
- seller_id (in general) : INT
- seller_name: STRING
  - name : STRING
- short_url: STRING
- short_description : STRING
  - price : DOUBLE
  - original_price : DOUBLE
  - discount: DOUBLE
  - discount_rate: DOUBLE
  - rating_average: DOUBLE
- review_count: INT
- review_text: STRING
- thumbnail_url : STRING
- day_ago_created : INT
- all_time_quantity_sold : INT
  - description: STRING
- images: []
  - large_url: STRING
    - medium_url: STRING
  - small_url: STRING
  - thumbnail_url: STRING
- warranty_policy: STRING
- warranty_info: []
  - name: STRING
  - value: STRING
  - url: STRING
- author: []
  - id: INT
  - original_id: INT
  - name: STRING
  - slug: STRING
- specifications: []
  - name: STRING
  - attributes: []
    - code: STRING
    - name: STRING
    - value: STRING
- configurable_options: []
  - code: STRING
  - name: STRING
  - position: INT
  - show_preview_image: BOOL
  - values: []
    - label: STRING
- highlight: []
  - item: STRING[]
  - title: STRING
- quantity_sold:
  - text: STRING
  - value: INT
- categories:
  - id: INT
  - original_id : INT
  - name: STRING
- brand: (with book: null)
  - id: INT
  - original_id: INT
  - name: STRING
  - slug: STRING

1. BOOK: GET DETAIL PRODUCT

2. MOBILE: GET DETAIL PRODUCT

3. CLOTHES: GET DETAIL PRODUCT
