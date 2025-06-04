
-- Use the `ref` function to select from other models

select *
from {{ ref('ro_genres') }}
where id = 1
