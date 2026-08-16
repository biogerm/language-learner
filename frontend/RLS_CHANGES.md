# RLS Policy Review & Optimization

## Identified Issues
The initial script `scripts/init_db.ts` created the following RLS policy for the `flashcard_progress` table:
```sql
CREATE POLICY "Users can manage their own progress" ON public.flashcard_progress 
FOR ALL USING (auth.uid() = user_id);
```

While `USING (auth.uid() = user_id)` is sufficient for `SELECT` and `DELETE` operations, using it alone for `FOR ALL` (which includes `INSERT` and `UPDATE`) is insecure. Without a `WITH CHECK` clause, a user can insert or update a row with another user's `user_id` if they manipulate the API request.

## Required Changes
To properly secure the `flashcard_progress` table, you should either add the `WITH CHECK` clause to the `FOR ALL` policy, or split the policies by operation.

### Recommended Fix (Single Policy)
```sql
DROP POLICY IF EXISTS "Users can manage their own progress" ON public.flashcard_progress;

CREATE POLICY "Users can manage their own progress" ON public.flashcard_progress
FOR ALL 
USING (auth.uid() = user_id) 
WITH CHECK (auth.uid() = user_id);
```

### Alternative Fix (Split Policies)
```sql
DROP POLICY IF EXISTS "Users can manage their own progress" ON public.flashcard_progress;

CREATE POLICY "Users can view their own progress" 
ON public.flashcard_progress FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own progress" 
ON public.flashcard_progress FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own progress" 
ON public.flashcard_progress FOR UPDATE 
USING (auth.uid() = user_id) 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own progress" 
ON public.flashcard_progress FOR DELETE 
USING (auth.uid() = user_id);
```

Please run one of the SQL scripts above in the Supabase SQL Editor, or update `scripts/init_db.ts` and re-run it.
