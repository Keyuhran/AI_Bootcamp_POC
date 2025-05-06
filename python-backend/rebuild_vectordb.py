if __name__ == "__main__":
    from logics.water_quality_query_handler import vectordb_acquire 
    vectordb_acquire('email_semantic_98', force_rebuild=True)
    vectordb_acquire('wq_reference', force_rebuild=True)
    print("✅ All vector DBs rebuilt.")
