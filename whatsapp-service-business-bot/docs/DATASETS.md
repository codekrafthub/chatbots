# Dataset Links and Data Management

This project includes a clean synthetic dataset inside the zip, so it runs immediately without downloading anything.

## Included datasets

### `data/menu.csv`

Restaurant menu data used by the bot:

- SKU
- item name
- category
- description
- price
- preparation time
- tags
- availability

### `data/faqs.csv`

FAQ automation data:

- question
- answer
- category
- keywords
- active flag

### `data/service_catalog.csv`

Generic service booking data:

- service code
- service name
- duration
- price
- description

### `data/sample_orders.csv`

Example external order analytics format.

---

## Public datasets you can cite/use

Use these as reference or optional extension datasets:

1. **Amazon Science FoodOrdering Dataset**  
   https://github.com/amazon-science/food-ordering-semantic-parsing-dataset  
   Good for food-ordering utterances and semantic parsing examples.

2. **Google Research Simulated Dialogue Dataset**  
   https://github.com/google-research-datasets/simulated-dialogue  
   Includes simulated restaurant-table booking dialogues.

3. **Maven Analytics Restaurant Orders Dataset**  
   https://mavenanalytics.io/data-playground/restaurant-orders  
   Useful for analytics dashboards and restaurant order BI examples.

4. **Hugging Face Bitext Restaurants LLM Chatbot Training Dataset**  
   https://huggingface.co/datasets/bitext/Bitext-restaurants-llm-chatbot-training-dataset  
   Useful for restaurant support intent/response examples.

5. **Kaggle Restaurant Chatbot Dataset**  
   https://www.kaggle.com/datasets/dmrcooode/restaurant-chatbot-dataset  
   Useful for FAQ-style restaurant chatbot examples.

6. **Kaggle Restaurant Delivery Orders Dataset**  
   https://www.kaggle.com/datasets/kbrakssa/restaurant-delivery-orders-dataset  
   Useful for delivery analytics and order forecasting.

---

## How to replace data for a real client

1. Ask the client for:
   - menu/services
   - prices
   - opening hours
   - delivery areas
   - FAQs
   - cancellation/refund rules
   - staff escalation phone/email

2. Edit `data/menu.csv` and `data/faqs.csv`.

3. Reset local database:

```bash
flask --app run.py reset-db
```

4. Test:

```text
menu
order
faq question
book
human
```

5. Deploy and connect WhatsApp.

---

## Recommended college dataset statement

> For this project, a synthetic restaurant menu and FAQ dataset was created in CSV format to represent client business data. Additional public datasets such as Amazon Science FoodOrdering, Google Simulated Dialogue, Maven Analytics Restaurant Orders, Hugging Face Bitext Restaurants, and Kaggle restaurant chatbot/order datasets can be used for extended testing, training or analytics.
