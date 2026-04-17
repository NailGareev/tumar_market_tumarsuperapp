package main

import (
	"encoding/json"
	"log"
	"net/http"
)

type Offer struct {
	ProductID    int     `json:"product_id"`
	SellerID     int     `json:"seller_id"`
	Price        int     `json:"price"`
	Stock        int     `json:"stock"`
	DeliveryDays int     `json:"delivery_days"`
	Warranty     int     `json:"warranty_months"`
	SellerRating float64 `json:"seller_rating"`
}

type rankRequest struct {
	Offers []Offer `json:"offers"`
}

type rankResponse struct {
	Offers []Offer `json:"offers"`
}

func decodeRequest(w http.ResponseWriter, r *http.Request) (*rankRequest, bool) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return nil, false
	}
	var req rankRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "bad request", http.StatusBadRequest)
		return nil, false
	}
	return &req, true
}

func writeResponse(w http.ResponseWriter, offers []Offer) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(rankResponse{Offers: offers})
}

func marketRankHandler(w http.ResponseWriter, r *http.Request) {
	req, ok := decodeRequest(w, r)
	if !ok {
		return
	}
	writeResponse(w, rankMarketOffers(req.Offers))
}

func sellerRankHandler(w http.ResponseWriter, r *http.Request) {
	req, ok := decodeRequest(w, r)
	if !ok {
		return
	}
	writeResponse(w, rankSellerOffers(req.Offers))
}

func healthHandler(w http.ResponseWriter, _ *http.Request) {
	w.WriteHeader(http.StatusOK)
	_, _ = w.Write([]byte("ok"))
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/rank/market", marketRankHandler)
	mux.HandleFunc("/rank/seller", sellerRankHandler)
	mux.HandleFunc("/health", healthHandler)

	addr := ":8090"
	log.Printf("go ranking service started on %s", addr)
	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatal(err)
	}
}
