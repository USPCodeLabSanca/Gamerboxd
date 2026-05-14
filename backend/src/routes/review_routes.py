from fastapi import Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from models.schemas import *
from services.security_services import *
from services.db_services import *
from utils.dependencies import get_conn, require_login

review_router = InferringRouter(prefix="/review", tags=["review"])

@cbv(review_router)
class NewReviewController:
    @review_router.post("/")
    async def create_review(self, review: ReviewIn, conn = Depends(get_conn), user_id = Depends(require_login)):
        try:
            review_for_insertion = is_review_insertion_valid(conn, review, user_id)

        except HTTPException as he:
            raise he
        
        except Exception as e:
            raise HTTPException(500, detail=str(e))
        
        review_creation_result = await DB_create_review(conn, review_for_insertion, user_id)

        if not review_creation_result.success or not review_creation_result.obj:
            raise HTTPException(500, str(review_creation_result.error))
        
        return JSONResponse({"message":review_creation_result.message}, status.HTTP_202_ACCEPTED)
                            
@cbv(review_router)       
class UpdateReviewController:
    @review_router.put("/{old_review_game}")
    async def update_review(self, old_review_game: str, new_review: ReviewIn, conn = Depends(get_conn), user_id = Depends(require_login)):
        try:
            review_for_insertion = is_review_updating_valid(conn, old_review_game, review, user_id)

        except HTTPException as he:
            raise he
        
        except Exception as e:
            raise HTTPException(500, detail=str(e))
        
        review_update_result = await DB_update_review(conn, old_review_game, user_id)

        if not review_update_result.success or not review_update_result.obj:
            raise HTTPException(500, str(review_update_result.error))
        
        return JSONResponse((review_update_result.obj).model_dump(), status.HTTP_202_ACCEPTED)

                                                       
@cbv(review_router)
class DeleteReviewController:
    @review_router.delete("/{review_game}")
    async def delete_review(self, review_game: str, conn = Depends(get_conn), user_id = Depends(get_conn)):
        review_delete_result = await DB_delete_review(conn, review_game, user_id)

        if not review_delete_result.success or not review_delete_result.obj:
            raise HTTPException(500, str(review_delete_result.error))
        
        return JSONResponse({"message":review_delete_result.message}, status.HTTP_202_ACCEPTED)